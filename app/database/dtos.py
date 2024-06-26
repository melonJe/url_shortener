from pydantic import BaseModel, Field


class UrlCreate(BaseModel):
    url: str
    expiry_days: int = Field(default=30)


class ShortUrlResponse(BaseModel):
    short_url: str


class UrlCountResponse(BaseModel):
    count: int
