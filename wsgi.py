#!/usr/bin/env python3
import sys
import os
import logging
from logging.handlers import RotatingFileHandler

# Resolve project base directory and log path
BASE_DIR = os.environ.get('NESPRESO_VIZ_PATH') or os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.environ.get('NESPRESO_VIZ_LOG') or os.path.join(BASE_DIR, 'wsgi.log')

# Configure logging (file if possible, else stderr)
try:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    handler = RotatingFileHandler(LOG_PATH, maxBytes=2_000_000, backupCount=3)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
except Exception:
    logging.basicConfig(level=logging.INFO)

logging.info("================== Initializing Nespreso Viz ===========================")
logging.info("Python executable: %s", sys.executable)
logging.info("Python version: %s", sys.version.replace('\n', ' '))

# Ensure the project directory is on sys.path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
logging.info("Updated sys.path (head): %s", sys.path[:3])

# Import Dash server as WSGI application
try:
    from nespreso_viz import server as application
    logging.info("WSGI application loaded successfully.")
except Exception as e:
    logging.exception("Failed to load WSGI application: %s", e)
    raise

logging.info("!!!!!!!!!! Done !!!!!!!!!!!!!!!!!")
