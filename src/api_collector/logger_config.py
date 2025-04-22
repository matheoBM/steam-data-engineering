import logging
import os

# Create logs directory if it doesn't exist
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Define logger
logger = logging.getLogger("shared_logger")
logger.setLevel(logging.INFO)

# Prevent duplicate handlers if the module is imported multiple times
if not logger.handlers:
    file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'), mode="a")
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)