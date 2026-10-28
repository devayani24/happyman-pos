"""
Entry point for the bundled HappyMan POS app.
"""

import sys
import os
import shutil
import logging
from pathlib import Path

from app.config import get_app_data_dir, DATABASE_PATH, SEED_DATA_PATH
from app.utils.logging_config import setup_logging
from app.utils.desktop_launcher import DesktopLauncher


# Setup logging as early as possible
setup_logging()
logger = logging.getLogger(__name__)


# ============================================================
# FIRST RUN HELPERS
# ============================================================

def get_exe_dir() -> Path:
    """Get the folder where the .exe (or dev script) is located."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def is_first_run() -> bool:
    """Return True if database doesn't exist yet."""
    return not DATABASE_PATH.exists()


def find_and_prepare_seed_file() -> bool:
    """Check both locations for seed_data.json."""
    appdata_path = SEED_DATA_PATH
    exe_path = get_exe_dir() / "seed_data.json"
    
    if appdata_path.exists():
        logger.info(f"Found seed_data.json at: {appdata_path}")
        return True
    
    if exe_path.exists():
        logger.info("Found seed_data.json next to app, copying to AppData")
        try:
            shutil.copy2(exe_path, appdata_path)
            logger.info(f"Copied to: {appdata_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to copy: {e}", exc_info=True)
            return False
    
    logger.warning("Seed file not found anywhere")
    return False


def show_missing_file_instructions():
    """Display instructions when seed file missing."""
    appdata_path = SEED_DATA_PATH
    exe_path = get_exe_dir() / "seed_data.json"
    
    print()
    print("=" * 60)
    print("SETUP REQUIRED")
    print("=" * 60)
    print()
    print("A required setup file 'seed_data.json' is missing.")
    print()
    print("OPTION 1 (Easier):")
    print(f"  Copy seed_data.json to: {exe_path}")
    print()
    print("OPTION 2:")
    print(f"  Copy seed_data.json to: {appdata_path.parent}")
    print()
    print("Then double-click the app again.")
    print("=" * 60)
    print()


def setup_database():
    """Create database on first run."""
    logger.info("Setting up database (first run)")
    try:
        from app.db.setup_db import setup
        setup()
        logger.info("Database created successfully")
    except Exception as e:
        logger.error(f"Database setup failed: {e}", exc_info=True)
        print(f"\nSetup failed: {e}")
        raise


# ============================================================
# MAIN
# ============================================================

def main():
    try:
        # First run flow
        if is_first_run():
            logger.info("First run detected")
            
            if not find_and_prepare_seed_file():
                show_missing_file_instructions()
                try:
                    input("Press Enter to close...")
                except (RuntimeError, EOFError):
                    import time
                    time.sleep(10)
                sys.exit(1)
            
            setup_database()
        else:
            logger.info("Database found, skipping first-run setup")
        
        # Import FastAPI app
        from app.main import app
        
        # Launch using reusable DesktopLauncher
        launcher = DesktopLauncher(
            app_name="HappyMan POS",
            exe_name="HappyManPos.exe",
            preferred_port=8000,
            app_data_dir=get_app_data_dir(),
        )
        
        launcher.run(app)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        print(f"Check logs at: {get_app_data_dir()}\\logs\\")
        try:
            input("Press Enter to close...")
        except (RuntimeError, EOFError):
            import time
            time.sleep(10)
        sys.exit(1)


if __name__ == "__main__":
    main()