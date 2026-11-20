"""Central configuration for the payroll pipeline. All paths and settings live here, so no other file hard-codes them."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project root: this file is src/payroll_pipeline/config.py, so go up 2 folders
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Read the .env file in the project root (secrets such as the API token)
load_dotenv(PROJECT_ROOT / ".env")

# --- Data locations ---
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
WAREHOUSE_DIR = DATA_DIR / "warehouse"

# --- Source API ---
DATASET_ID = "k397-673e"
API_URL = f"https://data.cityofnewyork.us/resource/{DATASET_ID}.json"
SOCRATA_APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN")  # None if not set

# --- Ingestion settings ---
PAGE_SIZE = 50_000  # rows per API request
REQUEST_TIMEOUT_SECONDS = 60  # give up on a request after this long
MAX_RETRIES = 3  # how many times to retry a failed request