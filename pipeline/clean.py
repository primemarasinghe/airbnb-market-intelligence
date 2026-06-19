import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

RAW_DIR = "data/raw/bangkok"
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"logs/clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


# LISTINGS 
def clean_listings():
    log.info("Cleaning listings...")
    df = pd.read_csv(os.path.join(RAW_DIR, "listings.csv"), low_memory=False)
    original_count = len(df)

    # Price: remove $ and commas, cast to float
    df["price"] = df["price"].astype(str).str.replace(r"[\$,]", "", regex=True).str.strip()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Date fields
    for col in ["last_review", "host_since", "first_review", "calendar_last_scraped", "last_scraped"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Host tenure in years
    if "host_since" in df.columns:
        df["host_tenure_years"] = ((datetime.now() - df["host_since"]).dt.days / 365).round(2)

    # Boolean fields
    bool_cols = ["host_is_superhost", "host_has_profile_pic", "host_identity_verified", "instant_bookable"]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].map({"t": True, "f": False})

    # Normalize room_type
    if "room_type" in df.columns:
        df["room_type"] = df["room_type"].str.strip().str.title()

    # Percentage fields
    for col in ["host_response_rate", "host_acceptance_rate"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("%", "").str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Flag invalid records
    df["flag_negative_price"] = df["price"] < 0
    df["flag_invalid_coords"] = ~(
        df["latitude"].between(12, 15) & df["longitude"].between(100, 101)
    )
    df["flag_zero_price"] = df["price"] == 0

    # Price per bedroom
    if "bedrooms" in df.columns:
        df["price_per_bedroom"] = (df["price"] / df["bedrooms"].replace(0, np.nan)).round(2)

    # Drop exact duplicates
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["id"])
    log.info(f"Duplicates removed: {before_dedup - len(df)}")

    # Missing value summary
    missing = df.isna().sum()
    top_missing = missing[missing > 0].sort_values(ascending=False).head(10)
    log.info(f"Top missing fields:\n{top_missing}")

    log.info(f"Listings: {original_count} → {len(df)} rows after cleaning")
    df.to_csv(os.path.join(OUT_DIR, "listings_clean.csv"), index=False)
    log.info("Saved listings_clean.csv")
    return df


# CALENDAR 
def clean_calendar():
    log.info("Cleaning calendar...")
    df = pd.read_csv(os.path.join(RAW_DIR, "calendar.csv"), low_memory=False)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["available"] = df["available"].map({"t": True, "f": False})
    df["price"] = df["price"].astype(str).str.replace(r"[\$,]", "", regex=True).str.strip()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["adjusted_price"] = df["adjusted_price"].astype(str).str.replace(r"[\$,]", "", regex=True).str.strip()
    df["adjusted_price"] = pd.to_numeric(df["adjusted_price"], errors="coerce")

    df["day_of_week"] = df["date"].dt.day_name()
    df["month"] = df["date"].dt.month
    df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"])

    log.info(f"Calendar rows: {len(df)}")
    df.to_csv(os.path.join(OUT_DIR, "calendar_clean.csv"), index=False)
    log.info("Saved calendar_clean.csv")
    return df


# REVIEWS 
def clean_reviews():
    log.info("Cleaning reviews...")
    df = pd.read_csv(os.path.join(RAW_DIR, "reviews.csv"), low_memory=False)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["comments"] = df["comments"].astype(str).str.strip()
    df = df.drop_duplicates()

    log.info(f"Reviews rows: {len(df)}")
    df.to_csv(os.path.join(OUT_DIR, "reviews_clean.csv"), index=False)
    log.info("Saved reviews_clean.csv")
    return df


def run():
    clean_listings()
    clean_calendar()
    clean_reviews()
    log.info("All cleaning complete.")

if __name__ == "__main__":
    run()