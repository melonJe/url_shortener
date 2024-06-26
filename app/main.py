from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import dtos
from app.database.postgres import get_db
from app.service import url_service
from app.url_scheduler import start_url_scheduler

# 애플리케이션 생성
app = FastAPI(
    title="URL Shortener Service",
    description="This service shortens long URLs into shorter ones.",
    version="1.0.0",
    contact={
        "name": "SangEun",
        "url": "http://localhost:8000"
    },
)


@app.on_event("startup")
def on_startup():
    start_url_scheduler()


@app.post("/shorten", response_model=dtos.ShortUrlResponse, summary="Create a short URL", tags=["URL Shortener"])
def create_short_url(url: dtos.UrlCreate, db: Session = Depends(get_db)):
    """
    입력받은 긴 URL을 고유한 단축 키로 변환하고 데이터베이스에 저장합니다.

    - **url**: 원본 URL
    - **expiry_days**: URL 만료 기간 (기본값: 30일)
    """
    try:
        short_key = url_service.create_short_url(db, url.url, url.expiry_days)
        return dtos.ShortUrlResponse(short_url=short_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/{short_key}", summary="Redirect to the original URL", tags=["URL Shortener"])
def get_original_url(short_key: str, db: Session = Depends(get_db)):
    """
    단축된 키를 통해 원본 URL로 리디렉션합니다.

    - **short_key**: 단축 키
    """
    original_url = url_service.get_original_url(db, short_key)
    if original_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    url_service.increment_access_count(short_key)
    response = RedirectResponse(url=original_url, status_code=301)
    # response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    # response.headers["Pragma"] = "no-cache"
    return response


@app.get("/stats/{short_key}", response_model=dtos.UrlCountResponse, summary="Get URL access count", tags=["URL Shortener"])
def get_url_stats(short_key: str, db: Session = Depends(get_db)):
    """
    단축 URL의 접근 통계를 제공합니다.

    - **short_key**: 단축 키
    """
    stats = url_service.get_url_access_count(db, short_key)
    if stats is None:
        raise HTTPException(status_code=404, detail="Stats not found")
    return dtos.UrlCountResponse(count=stats)
