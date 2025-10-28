from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# If your MySQL has no password, leave it blank like below:
DATABASE_URL = "mysql+pymysql://root@localhost/countrydb"

engine = create_engine(DATABASE_URL, echo=True)  # <- echo=True shows the SQL logs

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

