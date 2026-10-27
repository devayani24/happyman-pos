from datetime import datetime

def now_local() -> datetime:
    """Shop-local time, no offset, second precision."""
    return datetime.now().replace(microsecond=0)