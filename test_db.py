from country_currency_api.db import engine, Base, SessionLocal
from sqlalchemy import text  # ✅ Import text for raw SQL queries

def test_database():
    try:
        # Try creating tables
        Base.metadata.create_all(bind=engine)
        # Try opening a session
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # ✅ Wrap raw SQL with text()
        db.close()
        print("✅ Database connection successful!")
    except Exception as e:
        print("❌ Database connection failed!")
        print(e)

if __name__ == "__main__":
    test_database()
