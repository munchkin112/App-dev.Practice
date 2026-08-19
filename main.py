from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import httpx
from external_api import fetch_books, fetch_weather, load_fallback_books
from schemas import BookUpdate, ExternalBook, BookCreate, BookResponse, WeatherResponse
from database import books, save_books
from routers import books as books_router, external as external_router, system

tags_metadata = [
    {"name": "도서", "description": "도서 등록, 조회, 검색"},
    {"name": "외부 연동", "description": "Google Books와 날씨 API 연동"},
    {"name": "시스템", "description": "서버 상태 확인"},
]


app = FastAPI(
    title="도서 관리 API",
    description="도서를 등록·조회하고 외부 검색으로 정보를 가져오는 API",
    version="1.0.0",
    contact={
        "name": "홍길동",
        "email": "hong@example.com",},
    openapi_tags=tags_metadata,
)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(system.router)
app.include_router(external_router.router)
app.include_router(books_router.router)

def get_book_or_404(book_id: int) -> dict:
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")


# @app.get("/", tags=["시스템"], summary="API 홈 화면 조회")
# def read_root():
#     """도서 관리 API의 정적 홈 화면을 반환합니다."""
#     return FileResponse("static/index.html")


# @app.get("/health", tags=["시스템"], summary="서버 상태 확인")
# def health():
#     """서버가 정상적으로 응답하는지 확인할 상태값을 반환합니다."""
#     return {"status": "ok"}


# @app.get("/info", tags=["시스템"], summary="API 정보 조회")
# def info():
#     """도서 관리 API의 이름과 현재 버전을 반환합니다."""
#     return {"name": "도서 관리 API", "version": "0.2.0"}


# @app.get("/books", response_model=list[BookResponse], tags=["도서"], summary="도서 목록 조회")
def list_books():
    """현재 등록된 모든 도서를 반환합니다."""
    return books

# @app.post("/books",
#         response_model=BookResponse,
#         status_code=status.HTTP_201_CREATED,
#         tags=["도서"],
#         summary="도서 등록",
#         response_description="등록된 도서 정보",
#         responses={409: {"description": "중복된 도서입니다."}},)

def create_book(book: BookCreate):
    """
    새 도서를 등록합니다.

    - **title**: 1자 이상 100자 이하
    - **year**: 1900 이상 2100 이하
    - 같은 제목이 이미 있으면 409를 반환합니다.
    """

    for saved_book in books:
        if saved_book["title"] == book.title:
            raise HTTPException(status_code=409, detail="중복된 도서입니다.")

    new_book = {"id": max((item["id"] for item in books), default=0) + 1, **book.model_dump()}
    books.append(new_book)
    save_books()

    return new_book

# @app.put(
#     "/books/{book_id}",
#     tags=["도서"],
#     summary="도서 전체 수정",
#     responses={404: {"description": "도서를 찾을 수 없습니다"}},
#     response_model=BookResponse,)

def updatebook_(book_id: int, book: BookCreate):
    """도서 정보를 전면 교체합니다. 일부 수정 시 PATCH를 사용하세요."""
    old_book = get_book_or_404(book_id)
    new_book = {"id": book_id, **book.model_dump()}
    books[books.index(old_book)] = new_book
    save_books()
    return new_book

# @app.patch("/books/{book_id}",
#     response_model=BookResponse,
#     tags=["도서"],
#     summary="도서 부분 수정",
#     responses={404: {"description": "도서를 찾을 수 없습니다"}},)

def patch_book(book_id: int, patch: BookUpdate):
    """
    보낸 필드만 수정합니다. 보내지 않은 필드는 그대로 유지됩니다.
    """
    book = get_book_or_404(book_id)
    changes = patch.model_dump(exclude_unset=True)
    book.update(changes)
    save_books()
    return book

# @app.delete(
#     "/books/{book_id}",
#     status_code=204,
#     tags=["도서"],
#     summary="도서 삭제",
#     responses={404: {"description": "도서를 찾을 수 없습니다"}},
# )
def delete_book(book_id: int):
    """
    도서를 삭제합니다. 성공 시 본문 없이 204를 반환합니다.
    """
    book = get_book_or_404(book_id)
    books.remove(book)
    save_books()
    # for i, b in enumerate(books):
    #     if b["id"] == book_id:
    #         books.pop(i)
    #         return None
    # raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")

# @app.get("/books/search", tags=["도서"], summary="도서 제목 검색")
def search_books(keyword: str = ""):
    """
    제목에 검색어가 포함된 도서를 반환합니다.

    검색어가 비어 있으면 전체 도서 목록을 반환합니다.
    """
    if not keyword:
        return books
    return [book for book in books if keyword in book["title"]]


# @app.get("/books/filter", tags=["도서"], summary="도서 목록 필터링")
def filter_books(author: str = "", sort: str = ""):
    """
    저자와 정렬 기준을 적용한 도서 목록을 반환합니다.

    `author`가 있으면 저자가 정확히 일치하는 도서만 조회하고,
    `sort`가 `year`이면 출판 연도순으로 정렬합니다.
    """
    result = books
    if author:
        result = [book for book in result if book["author"] == author]
    if sort == "year":
        result = sorted(result, key=lambda book: book["year"])
    return result


# @app.get("/books/page", tags=["도서"], summary="도서 목록 페이지 조회")
def page_books(skip: int = 0, limit: int = 2):
    """전체 도서에서 `skip`만큼 건너뛴 뒤 최대 `limit`권을 반환합니다."""
    return books[skip : skip + limit]


# @app.get(
#     "/books/external",
#     response_model=list[ExternalBook],
#     tags=["외부 연동"],
#     summary="외부 도서 검색",
#     responses={
#         504: {"description": "외부 API 응답이 지연됩니다"},
#         502: {"description": "외부 API가 오류를 반환했습니다\n\n외부 API에 연결할 수 없습니다"},
#     },
# )
async def search_external_books(
    keyword: str,
    limit: int = 5,
    fallback: bool = False):
    """
    Google Books에서 검색어와 최대 결과 수에 맞는 도서를 조회합니다.

    외부 요청이 실패하고 `fallback`이 참이면 로컬 대체 도서 목록을 반환합니다.
    """

    try:
        return await fetch_books(keyword, limit)

    except httpx.TimeoutException:
        if fallback:
            return load_fallback_books()
        raise HTTPException(
            status_code=504,
            detail="외부 API 응답이 지연됩니다")
        
    except httpx.HTTPStatusError:
        if fallback:
            return load_fallback_books()
        raise HTTPException(
            status_code=502,
            detail="외부 API가 오류를 반환했습니다")
        
    except httpx.RequestError:
        if fallback:
            return load_fallback_books()
        raise HTTPException(
            status_code=502,
            detail="외부 API에 연결할 수 없습니다")

# @app.post(
#     "/books/from-external",
#     response_model=BookResponse,
#     status_code=201,
#     tags=["외부 연동"],
#     summary="외부 도서 등록",
#     responses={409: {"description": "이미 등록된 제목입니다"}},
# )

def create_from_external(book: ExternalBook):
    """
    외부 검색 형식의 도서를 내부 도서 목록에 등록합니다.

    출판 연도의 앞 네 자리를 사용할 수 없으면 2000년으로 저장하며,
    같은 제목이 이미 등록되어 있으면 409 오류를 반환합니다.
    """
    for b in books:
        if b["title"] == book.title:
            raise HTTPException(
                status_code=409,
                detail="이미 등록된 제목입니다")
            

    year = 2000

    if book.published_date[:4].isdigit():
        year = int(book.published_date[:4])

    new_id = max([b["id"] for b in books], default=0) + 1

    new_book = {
        "id": new_id,
        "title": book.title,
        "author": book.authors[0] if book.authors else "미상",
        "year": year,
        "tags": ["외부검색"],
        "publisher": None,
    }

    books.append(new_book)
    save_books()
    return new_book

# @app.get("/books/{book_id}", response_model=BookResponse, tags=["도서"], responses={404: {"description": "도서를 찾을 수 없습니다"}}, summary="도서 상세 조회")
def read_book(book_id: int):
    """도서 번호가 일치하는 도서를 반환하고, 없으면 404 오류를 반환합니다."""
    return get_book_or_404(book_id)



# @app.get("/weather", response_model=WeatherResponse, tags=["외부 연동"], summary="현재 날씨 조회")
async def weather(latitude: float = 36.8, longitude: float = 127.1):
    """지정한 위도와 경도의 현재 날씨를 외부 API에서 조회합니다."""
    return await fetch_weather(latitude, longitude)
