from fastapi import FastAPI

app = FastAPI()

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

books = [
    {"id": 1, "title": "파이썬 입문", "author": "김철수", "year": 2021},
    {"id": 2, "title": "FastAPI 실전", "author": "이영희", "year": 2023},
    {"id": 3, "title": "파이썬 웹개발", "author": "김철수", "year": 2022},
    {"id": 4, "title": "데이터 분석 기초", "author": "박민수", "year": 2020},
    {"id": 5, "title": "FastAPI로 배우는 백엔드", "author": "이영희", "year": 2024},
]

@app.get("/")
def read_root() : # c드라이브보다 상위 폴더가 없기 때문에 root 라고 표현한다(최상위)
    return {"message": "메인페이지"}

@app.get("/healthy") #데코 healthy는 호출하는 경로(api주소)
def health() :
    return {"status" : "healthy"}

@app.get("/info")
def info():
    return {"name": "도서 관리 API", "version": "0.1.0"}









#도서의 목록을 재공하는 엔드포인트
@app.get ("/books")
def list_books() :
    return books

#books 안에 search 기능을 넣은거기 때문에 순서를 반드시 맞춰야 된다.
@app.get("/books/search") 
def search_books(keyword: str = ""):
    if not keyword:
        return books
    return [b for b in books if keyword in b["title"]]



@app.get("/books/{book_id}")
def read_book(book_id : int) :
    for book in books :
        if book_id == book["id"] :
            return book
    return {"error" : "not found"}



