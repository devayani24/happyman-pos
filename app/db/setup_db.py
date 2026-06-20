import json
from pathlib import Path
from app.config import DATABASE_PATH
from app.db.database import get_connection
from app.models import SeedData

def init_schema():
  schema_path = Path(__file__).parent/"schema.sql"
  schema_sql = schema_path.read_text()

  with get_connection() as conn:
    conn.executescript(schema_sql)
  print(f"✓ Database initialized at {DATABASE_PATH}")

    

def load_seed_data() -> SeedData:
    """Load and validate seed_data.json.
    
    Raises ValidationError if the JSON doesn't match the SeedData schema.
    """
    seed_path = Path(__file__).parent / 'seed_data.json'
    
    with open(seed_path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    return SeedData(**raw)

def seed_categories(data: SeedData):
    """Insert categories. Idempotent — safe to run multiple times."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        for category in data.categories:
            cursor.execute(
                """
                INSERT OR IGNORE INTO categories (code, type, local_type_name)
                VALUES (?, ?, ?)
                """,
                (category.code, category.type, category.local_type_name)
            )
        
        print(f"✓ Seeded {len(data.categories)} categories")

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
    print("\nNext step: run the app with:")
    print("  uvicorn app.main:app --reload --port 8000")