from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import pymysql

# Tell SQLAlchemy to use PyMySQL as MySQLdb
pymysql.install_as_MySQLdb()

# Use Railway DATABASE_URL if available, otherwise fallback to local MySQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root@localhost/countrydb"  # local fallback
)

# If the env URL doesn't have +pymysql, add it
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
