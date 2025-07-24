# logger.py
import logging
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/expiry_watch.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("expiry_watch")
