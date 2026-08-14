import os

import httpx
from dotenv import load_dotenv

from schemas import WeatherResponse, GoogleBooks


load_dotenv()

GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_BOOKS_API_KEY:
    print("경고: GOOGLE_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")


# ============================================================
# Google Books API
# ============================================================

async def fetch_books(keyword: str, limit: int = 5) -> list[GoogleBooks]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                "q": keyword,
                "maxResults": limit,
                "key": GOOGLE_BOOKS_API_KEY,
            }
        )

        response.raise_for_status()
        data = response.json()

    result = []

    for item in data.get("items", []):
        book_info = item.get("volumeInfo", {})

        result.append(
            GoogleBooks(
                title=book_info.get("title", "제목없음"),
                authors=book_info.get("authors", []),
                published_date=book_info.get("publishedDate", "")
            )
        )

    return result


# ============================================================
# Open-Meteo API
# ============================================================

async def fetch_weather(
    latitude: float,
    longitude: float,
) -> WeatherResponse:

    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m",
            },
        )

        response.raise_for_status()

    data = response.json()

    return WeatherResponse(
        latitude=data["latitude"],
        longitude=data["longitude"],
        temperature=data["current"]["temperature_2m"],
        time=data["current"]["time"],
    )
