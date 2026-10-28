import logging
from logging.handlers import RotatingFileHandler
from app.config import get_app_data_dir

def setup_logging():
    """Configure rotating file logs"""
    log_dir = get_app_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "happyman_pos.log"
    
    handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB per file
        backupCount=5,                # Keep 5 old files
        encoding='utf-8'
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    # Also to console in dev mode
    import sys
    if not getattr(sys, 'frozen', False):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    logger.info("=" * 50)
    logger.info("HappyMan POS started")
    logger.info("=" * 50)