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

def load_seed_data():
    """Load and validate seed_data.json."""
    seed_path = Path(__file__).parent / 'seed_data.json'
    
    with open(seed_path, 'r', encoding='utf-8') as file:
        raw = json.load(file)
        return raw
    

def seed_data():
   

   categories,products = load_seed_data().keys()

   with get_connection() as conn:
    cursor = conn.cursor()
    for i in load_seed_data().get(categories):
        cursor.execute(
            """
            INSERT INTO categories (code,type,local_type_name) VALUES (?, ?, ?)
            """, (i.get('code'), i.get('type'), i.get('local_type_name'))
        )
    for i in load_seed_data().get(products):
        cursor.execute(
            """
            INSERT INTO products (product_code,name,local_name,category_code,sold_by,price,price_unit,price_unit_type,image,is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (i.get('product_code'), i.get('name'), i.get('local_name'), i.get('category_code'), i.get('sold_by'), i.get('price'), i.get('price_unit'), i.get('price_unit_type'), i.get('image'), i.get('is_active'))
        )

def setup():
    """Run the full database initialization."""
    print(f"Setting up database at {DATABASE_PATH}")
    
    print("→ Initializing schema...")
    init_schema()
    seed_data()
    
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