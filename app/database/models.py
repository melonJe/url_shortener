from datetime import datetime, timedelta

from sqlalchemy import Column, String, Integer, Date, BigInteger

from .postgres import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(BigInteger, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_key = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(Date, default=datetime.now)
    expires_at = Column(Date, default=lambda: datetime.now() + timedelta(days=30))
    access_count = Column(Integer, default=0)
