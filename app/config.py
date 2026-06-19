import os
from pathlib import Path

# ============= SHOP IDENTITY =============
# Change this per shop. Everything else can stay the same.

SHOP_ID = "HM"
SHOP_NAME = "HappyMan Ayyangar Sweet Stall"
SHOP_ADDRESS = "NorthVeli Street, Simmakkal, Madurai"
SHOP_PHONE = "+91 98765 43210"

# ============= DATABASE =============
# SQLite file path. Stored in /data, gitignored, lives next to the .exe in production.

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_PATH = DATA_DIR / f"{SHOP_ID}.db"