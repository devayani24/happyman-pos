"""
Sets up the database:
1. Creates tables from bundled schema.sql
2. Loads seed data from designated location (AppData when bundled)
"""

import sys
import json
from pathlib import Path
from app.config import DATABASE_PATH, SEED_DATA_PATH
from app.db.database import get_connection
from app.models import SeedData


def get_schema_path():
    """
    Get schema.sql path.
    - Bundled: from PyInstaller temp folder (sys._MEIPASS)
    - Dev: next to this file
    """
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / "app" / "db" / "schema.sql"
    else:
        return Path(__file__).parent / "schema.sql"


def init_schema():
    """Create tables from schema.sql."""
    schema_path = get_schema_path()
    schema_sql = schema_path.read_text(encoding='utf-8')

    with get_connection() as conn:
        conn.executescript(schema_sql)
    print(f"✓ Database initialized at {DATABASE_PATH}")


def load_seed_data() -> SeedData:
    """
    Load and validate seed_data.json from designated location.
    
    Raises FileNotFoundError if not present.
    Raises ValidationError if JSON doesn't match SeedData schema.
    """
    if not SEED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Seed data not found at: {SEED_DATA_PATH}\n"
            f"Place seed_data.json at this location before first run."
        )
    
    with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
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


def seed_products(data: SeedData):
    """Insert products, resolving category codes to IDs."""
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, code FROM categories")
        category_id_code = {row['code']: row['id'] for row in cursor.fetchall()}

        skipped_count = 0
        inserted_count = 0
        
        for product in data.products:
            category_id = category_id_code.get(product.category_code)

            if category_id is None:
                print(f"⚠️  Skipping {product.product_code}: category '{product.category_code}' not found")
                skipped_count += 1
                continue

            cursor.execute(
                """
                INSERT OR IGNORE INTO products (
                    product_code, name, local_name, category_id, sold_by,
                    price, price_unit, price_unit_type, image, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product.product_code,
                    product.name,
                    product.local_name,
                    category_id,
                    product.sold_by,
                    product.price,
                    product.price_unit,
                    product.price_unit_type,
                    product.image,
                    1 if product.is_active else 0,
                )
            )
            inserted_count += 1
        
        print(
            f"✓ Inserted {inserted_count} products"
            + (f", skipped {skipped_count}" if skipped_count else "")
        )


def setup():
    """Run the full database initialization."""
    print(f"Setting up database at {DATABASE_PATH}")
    
    print("→ Initializing schema...")
    init_schema()
    
    print("→ Loading seed data...")
    data = load_seed_data()
    
    print(f"→ Seeding {len(data.categories)} categories...")
    seed_categories(data)
    
    print(f"→ Seeding {len(data.products)} products...")
    seed_products(data)
    
    print("\n✓ Setup complete!")


if __name__ == "__main__":
    setup()
    print("\nNext step: run the app with:")
    print("  python run_app.py")