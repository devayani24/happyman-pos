import os
from pathlib import Path
from datetime import datetime

# ============= SHOP IDENTITY =============
# Change this per shop. Everything else can stay the same.

SHOP_ID = "HM1"
SHOP_NAME = "HappyMan Ayyangar Sweet Stall"
SHOP_ADDRESS = "NorthVeli Street, Simmakkal, Madurai"
SHOP_PHONE = "+91 98765 43210"

# ============= DATABASE =============
# SQLite file path. Stored in /data, gitignored, lives next to the .exe in production.

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_PATH = DATA_DIR / f"{SHOP_ID}.db"

# ============= SALES REPORT =============

now = datetime.now()
formatted = now.strftime("%Y-%m-%d_%H-%M-%S")

REPORT_DIR = PROJECT_ROOT.parent / "report"
REPORT_DIR.mkdir(exist_ok=True)
REPORT_PATH = REPORT_DIR / f"HappyMan_{SHOP_ID}_{formatted}.xlsx"
