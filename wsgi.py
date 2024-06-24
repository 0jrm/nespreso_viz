#!/home/ozavala/miniconda/envs/eoasweb/bin/python3
import sys
import os
import logging

# Configure logging
logging.basicConfig(filename='/var/www/virtualhosts/ozavala.coaps.fsu.edu/nespreso_viz/wsgi.log', level=logging.INFO)

#
logging.info("================== Initializing Nespreso Viz ===========================")

# Log the Python executable path
logging.info("Python executable: %s", sys.executable)

# Add the project directory to the sys.path
sys.path.insert(0, '/var/www/virtualhosts/ozavala.coaps.fsu.edu/nespreso_viz')

# Log the updated sys.path
logging.info("Updated sys.path: %s", sys.path)

try:
    from nespreso_viz import server as application
    # from hellodash import server as application
    logging.info("WSGI application loaded successfully. YEAH!")
except Exception as e:
    logging.exception("Failed to load WSGI application: %s", e)
    raise

logging.info("!!!!!!!!!! Done !!!!!!!!!!!!!!!!!")
