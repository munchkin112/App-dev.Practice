from fastapi import APIRouter, HTTPException, status

from database import books, save_books
from schemas import BookCreate, BookResponse, BookUpdate


router = APIRouter(prefix="/books")


def get_book_or_404(book_id: int) -> dict:
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")


@router.get(
    "",
    response_model=list[BookResponse],
    tags=["도서"],
    summary="도서 목록 조회",
)
def list_books():
    """현재 등록된 모든 도서를 반환합니다."""
    return books


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["도서"],
    summary="도서 등록",
    response_description="등록된 도서 정보",
    responses={409: {"description": "중복된 도서입니다."}},
)
def create_book(book: BookCreate):
    """새 도서를 등록하고, 같은 제목이 있으면 409 오류를 반환합니다."""
    for saved_book in books:
        if saved_book["title"] == book.title:
            raise HTTPException(status_code=409, detail="중복된 도서입니다.")

    new_book = {
        "id": max((item["id"] for item in books), default=0) + 1,
        **book.model_dump(),
    }
    books.append(new_book)
    save_books()
    return new_book


@router.get("/search", tags=["도서"], summary="도서 제목 검색")
def search_books(keyword: str = ""):
    """제목에 검색어가 포함된 도서를 반환합니다."""
    if not keyword:
        return books
    return [book for book in books if keyword in book["title"]]


@router.get("/filter", tags=["도서"], summary="도서 목록 필터링")
def filter_books(author: str = "", sort: str = ""):
    """저자와 정렬 기준을 적용한 도서 목록을 반환합니다."""
    result = books
    if author:
        result = [book for book in result if book["author"] == author]
    if sort == "year":
        result = sorted(result, key=lambda book: book["year"])
    return result


@router.get("/page", tags=["도서"], summary="도서 목록 페이지 조회")
def page_books(skip: int = 0, limit: int = 2):
    """전체 도서에서 일부 구간을 반환합니다."""
    return books[skip : skip + limit]


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    tags=["도서"],
    summary="도서 전체 수정",
    responses={404: {"description": "도서를 찾을 수 없습니다"}},
)
def updatebook_(book_id: int, book: BookCreate):
    """도서 정보를 전면 교체합니다. 일부 수정 시 PATCH를 사용하세요."""
    old_book = get_book_or_404(book_id)
    new_book = {"id": book_id, **book.model_dump()}
    books[books.index(old_book)] = new_book
    save_books()
    return new_book


@router.patch(
    "/{book_id}",
    response_model=BookResponse,
    tags=["도서"],
    summary="도서 부분 수정",
    responses={404: {"description": "도서를 찾을 수 없습니다"}},
)
def patch_book(book_id: int, patch: BookUpdate):
    """요청으로 전달한 필드만 수정합니다."""
    book = get_book_or_404(book_id)
    changes = patch.model_dump(exclude_unset=True)
    book.update(changes)
    save_books()
    return book


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["도서"],
    summary="도서 삭제",
    responses={404: {"description": "도서를 찾을 수 없습니다"}},
)
def delete_book(book_id: int):
    """도서를 삭제하고 본문 없이 응답합니다."""
    book = get_book_or_404(book_id)
    books.remove(book)
    save_books()


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    tags=["도서"],
    summary="도서 상세 조회",
    responses={404: {"description": "도서를 찾을 수 없습니다"}},
)
def read_book(book_id: int):
    """도서 번호가 일치하는 도서를 반환합니다."""
    return get_book_or_404(book_id)
