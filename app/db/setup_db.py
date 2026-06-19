import json
import sqlite3
from pathlib import Path
from app.config import DATABASE_PATH,SHOP_ID
from app.db.database import get_connection

def init_schema():
  schema_path = Path(__file__).parent/"schema.sql"
  schema_sql = schema_path.read_text()

  with get_connection() as conn:
    conn.executescript(schema_sql)
    print(f"✓ Database initialized at {DATABASE_PATH}")

def setup():
    """Run the full database initialization."""
    print(f"Setting up database at {DATABASE_PATH}")
    
    print("→ Initializing schema...")
    init_schema()
    
    # print("→ Loading seed data...")
    # seed = load_seed_data()
    
    # print(f"→ Seeding {len(seed.categories)} categories...")
    # seed_categories(seed)
    
    # print(f"→ Seeding {len(seed.products)} products...")
    # seed_products(seed)
    
    print("\n✓ Setup complete!")
if __name__ == "__main__":


    setup()

    print("\n✓ Setup complete!")
    print("\nNext step: run the app with:")
    print("  uvicorn app.main:app --reload --port 8000")