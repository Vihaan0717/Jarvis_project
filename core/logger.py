import logging
import os

# Create a folder to store JARVIS's diaries (logs)
os.makedirs("logs", exist_ok=True)

def get_logger(name):
    """JARVIS's centralized logging system."""
    logger = logging.getLogger(name)
    
    # Only set it up if it hasn't been set up already
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # This formats the text so it looks neat and includes the exact time
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 1. Print messages to your terminal (so we can see them live)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 2. Save messages to a permanent file (his diary)
        file_handler = logging.FileHandler("logs/jarvis_system.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger