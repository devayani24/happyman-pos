"""
Entry point for the bundled HappyMan POS app.

First-run behavior:
1. Checks for seed_data.json in AppData location
2. If not found there, checks next to the .exe
3. If found next to .exe: auto-copies to AppData
4. If not found anywhere: shows helpful error with instructions

Subsequent runs:
- Skips setup (database already exists)
- Starts backend and opens browser
"""

import sys
import os
import time
import shutil
import webbrowser
import threading
import uvicorn
from pathlib import Path
from app.config import get_app_data_dir, DATABASE_PATH, SEED_DATA_PATH


# ============================================================
# PATH HELPERS
# ============================================================

def get_app_data_dir():
    """
    Get the app's persistent data directory.
    - Bundled: Uses Windows AppData folder
    - Dev mode: Uses project folder
    """
    if getattr(sys, 'frozen', False):
        appdata = Path(os.environ.get('LOCALAPPDATA', Path.home()))
        app_dir = appdata / "HappyManPos"
    else:
        app_dir = Path(__file__).parent
    
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_database_path():
    return DATABASE_PATH


def get_appdata_seed_path():
    return SEED_DATA_PATH


def get_exe_dir():
    """Get the folder where the .exe (or dev script) is located."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent


def get_exe_seed_path():
    """The alternative location: next to the .exe."""
    return get_exe_dir() / "seed_data.json"


# ============================================================
# FIRST RUN CHECKS (Way 2 — friendly two-location check)
# ============================================================

def is_first_run():
    """Return True if database doesn't exist yet."""
    return not get_database_path().exists()


def find_and_prepare_seed_file():
    """
    Way 2: Check both locations for seed_data.json.
    
    Priority:
      1. AppData location (designated permanent home)
      2. Next to .exe (auto-copy to AppData if found here)
    
    Returns:
      True  - seed file is ready at AppData location
      False - seed file not found anywhere, user must provide it
    """
    appdata_path = get_appdata_seed_path()
    exe_path = get_exe_seed_path()
    
    # Case 1: Already at designated location
    if appdata_path.exists():
        print(f"✓ Found seed_data.json at: {appdata_path}")
        return True
    
    # Case 2: Found next to .exe — auto-copy to designated location
    if exe_path.exists():
        print(f"✓ Found seed_data.json next to app.")
        print(f"  Copying to permanent location...")
        try:
            shutil.copy2(exe_path, appdata_path)
            print(f"  Copied to: {appdata_path}")
            print()
            return True
        except Exception as e:
            print(f"✗ Failed to copy: {e}")
            return False
    
    # Case 3: Not found anywhere
    return False


def show_missing_file_instructions():
    """Display clear instructions when seed file is missing."""
    appdata_path = get_appdata_seed_path()
    exe_path = get_exe_seed_path()
    
    print()
    print("=" * 60)
    print("SETUP REQUIRED")
    print("=" * 60)
    print()
    print("This is your first time running HappyMan POS.")
    print("A required setup file 'seed_data.json' is missing.")
    print()
    print("You have TWO options to fix this:")
    print()
    print("─" * 60)
    print("OPTION 1 (Easier):")
    print("─" * 60)
    print()
    print(f"  1. Copy seed_data.json next to the app:")
    print(f"     {exe_path}")
    print()
    print("  2. Close this window")
    print("  3. Double-click HappyManPos.exe again")
    print("     (The app will copy the file automatically)")
    print()
    print("─" * 60)
    print("OPTION 2 (Manual):")
    print("─" * 60)
    print()
    print(f"  1. Copy seed_data.json to this exact location:")
    print(f"     {appdata_path.parent}")
    print()
    print("  2. Close this window")
    print("  3. Double-click HappyManPos.exe again")
    print()
    print("=" * 60)
    print()
    print("The seed_data.json file was provided by Devayani.")
    print("Contact her if you can't find it.")
    print()


# ============================================================
# DATABASE SETUP
# ============================================================

def setup_database():
    """Create database and load seed data on first run."""
    print()
    print("Setting up database (first run)...")
    print("This may take a few moments...")
    print()
    
    try:
        from app.db.setup_db import setup
        setup()
        print()
        print("✓ Database created successfully!")
        print()
    except Exception as e:
        print()
        print("=" * 60)
        print("SETUP FAILED")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("Please contact Devayani for help.")
        print()
        input("Press Enter to close...")
        sys.exit(1)


# ============================================================
# BROWSER LAUNCHER
# ============================================================

def open_browser_after_delay():
    """Wait for backend to start, then open browser in app mode."""
    time.sleep(3)
    print("Opening browser...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    
    chrome_found = None
    for path in chrome_paths:
        expanded = os.path.expandvars(path)
        if Path(expanded).exists():
            chrome_found = expanded
            break
    
    url = "http://localhost:8000/"
    
    if chrome_found:
        # Chrome app mode: no address bar, looks like native app
        os.system(f'"{chrome_found}" --app={url} --new-window')
    else:
        print("Chrome not found. Opening default browser.")
        webbrowser.open(url)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("HappyMan POS")
    print("=" * 60)
    print()
    
    # First run flow
    if is_first_run():
        print("First run detected.")
        print()
        
        # Way 2: Check both locations for seed file
        seed_ready = find_and_prepare_seed_file()
        
        if not seed_ready:
            # Seed file not found anywhere
            show_missing_file_instructions()
            input("Press Enter to close...")
            sys.exit(1)
        
        # Seed file is ready — create database
        setup_database()
    else:
        print("Database found. Starting app...")
    
    # Open browser in background
    browser_thread = threading.Thread(
        target=open_browser_after_delay,
        daemon=True
    )
    browser_thread.start()
    
    # Start FastAPI server
    print()
    print(f"Server running at http://localhost:8000")
    print("Close this window to shut down the app.")
    print("=" * 60)
    print()
    
    from app.main import app
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()