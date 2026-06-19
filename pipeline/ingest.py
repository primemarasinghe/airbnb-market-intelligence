import os
import requests
import gzip
import shutil
import logging
import json
from datetime import datetime

CITY = "Bangkok"
BASE_URL = "https://data.insideairbnb.com/thailand/central-thailand/bangkok/2025-09-26"

FILES = {
    "listings_summary": "listings.csv.gz",
    "listings_summary": "data/listings.csv.gz",
    "calendar": "data/calendar.csv.gz",
    "reviews": "data/reviews.csv.gz",
    "neighbourhoods": "visualisations/neighbourhoods.csv",
    "neighbourhoods_geojson": "visualisations/neighbourhoods.geojson",
}

 # Directory to store raw data
RAW_DIR = os.path.join("data", "raw", CITY)
LOG_DIR = "logs"

#logging setup
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,   #Log level Format
    format="%(asctime)s [%(levelname)s] %(message)s", 
    handlers=[
        logging.FileHandler(f"logs/ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

def download_file(url, dest_path, retries=3):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    for attempt in range(1, retries + 1):
        try:
            log.info(f"Downloading {url} (attempt {attempt})")
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                f.write(r.content)
            log.info(f"Saved to {dest_path}")
            return True
        except Exception as e:
            log.warning(f"Attempt {attempt} failed: {e}")
    log.error(f"All retries failed for {url}")
    return False

def extract_gz(gz_path):
    out_path = gz_path.replace(".gz", "")
    try:
        with gzip.open(gz_path, "rb") as f_in:
            with open(out_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        log.info(f"Extracted to {out_path}")
    except Exception as e:
        log.error(f"Extraction failed for {gz_path}: {e}")


def save_metadata(meta):
    path = os.path.join(RAW_DIR, "ingest_metadata.json")
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)
    log.info(f"Metadata saved to {path}")


def run():
    log.info(f"Starting ingestion for city: {CITY}")
    metadata = {
        "city": CITY,
        "ingested_at": datetime.now().isoformat(),
        "source_url": BASE_URL,
        "files": {}
    }

    for key, filename in FILES.items():
        url = f"{BASE_URL}/{filename}"
        dest = os.path.join(RAW_DIR, filename)
        success = download_file(url, dest)
        metadata["files"][key] = {
            "filename": filename,
            "status": "success" if success else "failed",
            "path": dest
        }
        if success and filename.endswith(".gz"):
            extract_gz(dest)

    save_metadata(metadata)
    log.info("Ingestion complete.")


if __name__ == "__main__":
    run()