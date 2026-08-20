"""
Configuration for HappyMan POS.
Handles paths for both development and bundled (.exe) modes.
"""

import os
import sys
from pathlib import Path
from datetime import datetime


# ============= SHOP IDENTITY =============
# Change this per shop. Everything else can stay the same.

SHOP_ID = "HM1"


# ============= PATH HELPERS =============

def is_bundled():
    """Return True if running as PyInstaller bundled app."""
    return getattr(sys, 'frozen', False)


def get_app_data_dir():
    """
    Get the directory for persistent app data.
    - Bundled: Windows AppData (persists across app updates)
    - Dev: project root folder
    """
    if is_bundled():
        appdata = Path(os.environ.get('LOCALAPPDATA', Path.home()))
        return appdata / "HappyManPos"
    else:
        # Dev: use project root (this file's grandparent)
        return Path(__file__).parent.parent


# ============= PROJECT ROOT =============

PROJECT_ROOT = Path(__file__).parent.parent


# ============= DATABASE =============
# SQLite file path. Lives in AppData when bundled, in project /data during dev.

DATA_DIR = get_app_data_dir() / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = DATA_DIR / f"{SHOP_ID}.db"


# ============= SEED DATA =============
# Where seed_data.json lives for first-time setup.

SEED_DATA_PATH = get_app_data_dir() / "seed_data.json"


# ============= SALES REPORT =============
# Directory only — filename generated at report time.

REPORT_DIR = get_app_data_dir() / "report"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def get_report_path():
    """
    Generate a new report path with current timestamp.
    Call this each time a report is generated (not at import time).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return REPORT_DIR / f"HappyMan_{SHOP_ID}_{timestamp}.xlsx"