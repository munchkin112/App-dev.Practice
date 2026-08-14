from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from external_api import fetch_books, fetch_weather
from schemas import BookCreate, BookResponse, GoogleBooks, WeatherResponse


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

books = [
    {"id": 1, "title": "파이썬 입문", "author": "김철수", "year": 2021},
    {"id": 2, "title": "FastAPI 실전", "author": "이영희", "year": 2023},
    {"id": 3, "title": "파이썬 웹개발", "author": "김철수", "year": 2022},
    {"id": 4, "title": "데이터 분석 기초", "author": "박민수", "year": 2020},
    {"id": 5, "title": "FastAPI로 배우는 백엔드", "author": "이영희", "year": 2024},
]


@app.get("/")
def read_root():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/info")
def info():
    return {"name": "도서 관리 API", "version": "0.2.0"}


@app.get("/books", response_model=list[BookResponse])
def list_books():
    return books


@app.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_book(book: BookCreate):
    for saved_book in books:
        if saved_book["title"] == book.title:
            raise HTTPException(status_code=409, detail="중복된 도서입니다.")

    new_book = {"id": max((item["id"] for item in books), default=0) + 1, **book.model_dump()}
    books.append(new_book)
    return new_book


@app.get("/books/search")
def search_books(keyword: str = ""):
    if not keyword:
        return books
    return [book for book in books if keyword in book["title"]]


@app.get("/books/filter")
def filter_books(author: str = "", sort: str = ""):
    result = books
    if author:
        result = [book for book in result if book["author"] == author]
    if sort == "year":
        result = sorted(result, key=lambda book: book["year"])
    return result


@app.get("/books/page")
def page_books(skip: int = 0, limit: int = 2):
    return books[skip : skip + limit]


@app.get("/books/external", response_model=list[GoogleBooks])
async def search_external_books(keyword: str, limit: int = 5):
    return await fetch_books(keyword, limit)


@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")


@app.get("/weather", response_model=WeatherResponse)
async def weather(latitude: float = 36.8, longitude: float = 127.1):
    return await fetch_weather(latitude, longitude)
