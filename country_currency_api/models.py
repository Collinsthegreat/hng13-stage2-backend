from sqlalchemy import Column, Integer, String, Float, DateTime, func
from db import Base  # 👈 this is the fix!

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    capital = Column(String(255), nullable=True)
    region = Column(String(100), nullable=True)
    population = Column(Integer, nullable=False)
    currency_code = Column(String(10), nullable=True, index=True)
    exchange_rate = Column(Float, nullable=True)
    estimated_gdp = Column(Float, nullable=True)
    flag_url = Column(String(512), nullable=True)
    last_refreshed_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())


class Metadata(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(255), nullable=True)
