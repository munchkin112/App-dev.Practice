import asyncio
import time

import httpx
from fastapi import APIRouter, HTTPException, status

from database import books, save_books
from external_api import fetch_books, fetch_weather, load_fallback_books
from schemas import BookResponse, ExternalBook, WeatherResponse


router = APIRouter(tags=["외부 연동"])


@router.get(
    "/weather",
    response_model=WeatherResponse,
    summary="현재 날씨 조회",
    responses={
        502: {
            "description": "외부 API가 오류를 반환했습니다\n\n외부 API에 연결할 수 없습니다"
        },
        504: {"description": "외부 API 응답이 지연됩니다"},
    },
)
async def weather(latitude: float = 36.8, longitude: float = 127.1):
    """좌표로 현재 날씨를 조회합니다."""
    try:
        return await fetch_weather(latitude, longitude)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="외부 API가 오류를 반환했습니다")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")


@router.get(
    "/books/external/multi",
    summary="여러 키워드 동시 검색",
    responses={
        502: {
            "description": "외부 API가 오류를 반환했습니다\n\n외부 API에 연결할 수 없습니다"
        },
        504: {"description": "외부 API 응답이 지연됩니다"},
    },
)
async def search_multi(keywords: str = "python,fastapi,django"):
    """쉼표로 구분한 여러 키워드를 동시에 검색합니다."""
    words = [word.strip() for word in keywords.split(",") if word.strip()]

    start = time.perf_counter()
    try:
        results = await asyncio.gather(*(fetch_books(word) for word in words))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="외부 API가 오류를 반환했습니다")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")

    elapsed = round(time.perf_counter() - start, 2)
    return {"elapsed_seconds": elapsed, "results": results}


@router.get(
    "/books/external",
    response_model=list[ExternalBook],
    summary="Google Books 검색",
    responses={
        502: {
            "description": "외부 API가 오류를 반환했습니다\n\n외부 API에 연결할 수 없습니다"
        },
        504: {"description": "외부 API 응답이 지연됩니다"},
    },
)
async def search_external_books(
    keyword: str,
    limit: int = 5,
    fallback: bool = False,
):
    """Google Books에서 도서를 검색합니다."""
    try:
        return await fetch_books(keyword, limit)
    except httpx.TimeoutException:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
    except httpx.HTTPStatusError:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=502, detail="외부 API가 오류를 반환했습니다")
    except httpx.RequestError:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")


@router.post(
    "/books/from-external",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="외부 검색 결과 등록",
    responses={409: {"description": "이미 등록된 제목입니다"}},
)
def create_from_external(book: ExternalBook):
    """Google Books 검색 결과를 내부 도서 목록에 등록합니다."""
    for saved_book in books:
        if saved_book["title"] == book.title:
            raise HTTPException(status_code=409, detail="이미 등록된 제목입니다")

    year = 2000
    if book.published_date[:4].isdigit():
        year = int(book.published_date[:4])

    new_book = {
        "id": max((item["id"] for item in books), default=0) + 1,
        "title": book.title,
        "author": book.authors[0] if book.authors else "미상",
        "year": year,
        "tags": ["외부검색"],
        "publisher": None,
    }
    books.append(new_book)
    save_books()
    return new_book
