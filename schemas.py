from pydantic import BaseModel, ConfigDict, Field, field_validator


class Publisher(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        description="출판사 이름",
        examples=["한빛미디어"],
    )
    city: str = Field(
        min_length=1,
        max_length=100,
        description="출판사 소재지",
        examples=["서울"],
    )


class BookCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "처음 시작하는 FastAPI",
                    "author": "빌 루바노빅",
                    "year": 2025,
                    "tags": ["Python", "웹 개발"],
                    "publisher": {
                        "name": "한빛미디어",
                        "city": "서울",
                    },
                }
            ]
        }
    )

    title: str = Field(min_length=1, max_length=100,
        description="도서 제목",
        examples=["처음 시작하는 FastAPI"])

    author: str = Field(min_length=1,max_length=50,
        description="도서 저자",
        examples=["빌 루바노빅"])

    year: int = Field(ge=1900,le=2100,
        description="출판 연도",
        examples=[2025])

    tags: list[str] = Field(default_factory=list,
        description="분류 태그",
        examples=[["Python", "웹 개발"]])

    publisher: Publisher | None = Field(
        default=None,
        description="출판사 정보",
        examples=[{"name": "한빛미디어", "city": "서울"}],
    )
    
    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("제목은 공백일 수 없습니다")

        return value


class BookResponse(BookCreate):
    id: int = Field(description="도서 식별자", examples=[1])


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    author: str | None = Field(default=None, min_length=1, max_length=50)
    year  : int | None = Field(default=None, ge=1900, le=2026,
                            description="출판 연도",
                            examples=[2024],)
    tags : list[str] | None = Field(default=None,
                                description="도서 태그 목록",
                                examples=["python", "web"],)
    publisher : Publisher | None = Field(default=None, description="출판사 정보")


class WeatherResponse(BaseModel):
    latitude: float = Field(description="위도", examples=[37.5665])
    longitude: float = Field(description="경도", examples=[126.978])
    temperature: float = Field(description="현재 기온", examples=[24.3])
    time: str = Field(description="관측 시각", examples=["2026-08-18T14:00"])


class GoogleBooks(BaseModel):
    title: str = Field(description="도서 제목", examples=["Do it! 점프 투 파이썬"])
    authors: list[str] = Field(
        default_factory=list,
        description="저자 목록",
        examples=[["박응용"]],
    )
    published_date: str = Field(
        default="",
        description="출판일",
        examples=["2019"],
    )

class ExternalBook(BaseModel):
    title: str = Field(description="도서 제목", examples=["Do it! 점프 투 파이썬"])
    authors: list[str] = Field(
        default_factory=list,
        description="저자 목록",
        examples=[["박응용"]],
    )
    published_date: str = Field(
        default="",
        description="출판일",
        examples=["2019"],
    )
