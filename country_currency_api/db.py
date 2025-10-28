import os
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Tell SQLAlchemy to use PyMySQL as MySQLdb
pymysql.install_as_MySQLdb()

# Get DATABASE_URL from environment or fallback
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root@localhost/countrydb")

# Force PyMySQL in the URL if missing
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
