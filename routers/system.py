from fastapi import APIRouter ,HTTPException
from database import books, save_books


router = APIRouter(tags=["시스템"])


@router.get("/", summary="루트")
def read_root():
    """API의 기본 메시지를 반환합니다."""
    return {"message": "Hello world!"}


@router.get("/health", summary="서버 상태 확인")
def health():
    """서버가 정상적으로 응답하는지 확인합니다."""
    return {"status": "ok"}


@router.get("/info", summary="앱 정보")
def info():
    """API의 이름과 버전을 반환합니다."""
    return {"name": "도서 관리 API", "version": "1.0.0"}

# 도서 목록 경로는 routers/books.py로 분리되어 중복 코드를 주석 처리했습니다.
# @router.get("/books", response_model=list[BookResponse], tags=["도서"], summary="도서 목록 조회")
# def list_books():
#     """현재 등록된 모든 도서를 반환합니다."""
#     return books
