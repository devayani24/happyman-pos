from app.db.database import init_db
from app.config import DATABASE_PATH, SHOP_ID


if __name__ == "__main__":

    print(f"  Setting up database for: {SHOP_ID}")
    print(f"  Path: {DATABASE_PATH}")


    init_db()

    print("\n✓ Setup complete!")
    print("\nNext step: run the app with:")
    print("  uvicorn app.main:app --reload --port 8000")