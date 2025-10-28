from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use Railway DATABASE_URL if available, otherwise fallback to local MySQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root@localhost/countrydb"  # local fallback
)

engine = create_engine(DATABASE_URL, echo=True)  # echo=True shows SQL logs

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
