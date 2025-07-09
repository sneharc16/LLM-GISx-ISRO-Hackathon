# config.py

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEOSERVER_URL = os.getenv("GEOSERVER_URL")
GEOSERVER_USER = os.getenv("GEOSERVER_USER")
GEOSERVER_PASS = os.getenv("GEOSERVER_PASS")
POSTGIS_DSN = os.getenv("POSTGIS_DSN")

# Fallback to a default data directory if not specified
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.getcwd(), "data"))
