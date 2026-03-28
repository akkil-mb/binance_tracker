from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime, timezone

class CryptoCurrency(Base):
    __tablename__ = "crypto_currency"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    symbol = Column(String(20), unique=True, nullable=False)

    def __str__(self):
        return f"{self.name} : {self.symbol}"


class CryptoTracker(Base):
    __tablename__ = "crypto_tracker"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), ForeignKey("crypto_currency.symbol"), unique=True, nullable=False)
    last_price = Column(Numeric(precision=18, scale=8), nullable=True)
    one_day_change = Column(Numeric(precision=8, scale=4), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=True)  # event time from Binance
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
