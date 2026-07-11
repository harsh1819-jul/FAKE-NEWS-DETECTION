import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    """
    Sets up a rotating file logger for TruthLens.
    Logs are stored in the 'logs/' folder.
    """
    # Ensure logs directory exists relative to the project root
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(root_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "truthlens.log")
    
    logger = logging.getLogger("TruthLens")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        
        # Max size 5MB, keep 3 backup files
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Stream to stdout/console as well
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger

# Globally accessible logger instance
logger = setup_logger()
