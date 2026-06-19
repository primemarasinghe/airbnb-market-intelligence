import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

OUT_DIR = "data/processed"
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def build_enriched_listings():
    log.info("Building enriched listings master table...")
    listings = pd.read_csv(os.path.join(OUT_DIR, "listings_clean.csv"), low_memory=False)

    #Neighbourhood aggregates ---
    neighbourhood_agg = listings.groupby("neighbourhood_cleansed").agg(
        neighbourhood_median_price=("price", "median"),
        neighbourhood_listing_count=("id", "count"),
        neighbourhood_avg_rating=("review_scores_rating", "mean"),
        neighbourhood_avg_reviews=("number_of_reviews", "mean")
    ).round(2).reset_index()

    listings = listings.merge(neighbourhood_agg, on="neighbourhood_cleansed", how="left")

    # Occupancy from calendar 
    log.info("Computing occupancy rates from calendar...")
    cal = pd.read_csv(os.path.join(OUT_DIR, "calendar_clean.csv"),
                      usecols=["listing_id", "available", "price", "is_weekend", "month"],
                      low_memory=False)

    occupancy = cal.groupby("listing_id").agg(
        total_days=("available", "count"),
        booked_days=("available", lambda x: (x == False).sum()),
        avg_calendar_price=("price", "mean")
    ).reset_index()
    occupancy["occupancy_rate"] = (occupancy["booked_days"] / occupancy["total_days"]).round(4)
    occupancy["estimated_annual_revenue"] = (
        occupancy["occupancy_rate"] * occupancy["avg_calendar_price"] * 365
    ).round(2)
    occupancy.rename(columns={"listing_id": "id"}, inplace=True)

    listings = listings.merge(occupancy, on="id", how="left")

    # --- Host segmentation ---
    host_portfolio = listings.groupby("host_id")["id"].count().reset_index()
    host_portfolio.columns = ["host_id", "host_listing_count_actual"]
    host_portfolio["host_type"] = host_portfolio["host_listing_count_actual"].apply(
        lambda x: "Single" if x == 1 else ("Small Multi" if x <= 5 else "Commercial")
    )
    listings = listings.merge(host_portfolio, on="host_id", how="left")

    # --- Review frequency (reviews per month) ---
    if "number_of_reviews" in listings.columns and "host_tenure_years" in listings.columns:
        listings["review_frequency"] = (
            listings["number_of_reviews"] / (listings["host_tenure_years"] * 12 + 0.01)
        ).round(3)

    log.info(f"Enriched listings shape: {listings.shape}")
    listings.to_csv(os.path.join(OUT_DIR, "listings_enriched.csv"), index=False)
    log.info("Saved listings_enriched.csv")
    return listings


def build_star_schema():
    log.info("Building star schema...")
    df = pd.read_csv(os.path.join(OUT_DIR, "listings_enriched.csv"), low_memory=False)
    os.makedirs(os.path.join(OUT_DIR, "star_schema"), exist_ok=True)

    # --- DIM: Host ---
    dim_host = df[[
        "host_id", "host_name", "host_since", "host_is_superhost",
        "host_response_rate", "host_acceptance_rate", "host_identity_verified",
        "host_listing_count_actual", "host_type", "host_tenure_years"
    ]].drop_duplicates(subset=["host_id"]).reset_index(drop=True)
    dim_host.to_csv(os.path.join(OUT_DIR, "star_schema", "dim_host.csv"), index=False)

    # --- DIM: Location ---
    dim_location = df[[
        "neighbourhood_cleansed", "latitude", "longitude",
        "neighbourhood_median_price", "neighbourhood_listing_count", "neighbourhood_avg_rating"
    ]].drop_duplicates(subset=["neighbourhood_cleansed"]).reset_index(drop=True)
    dim_location["location_id"] = dim_location.index + 1
    dim_location.to_csv(os.path.join(OUT_DIR, "star_schema", "dim_location.csv"), index=False)

    # --- DIM: Property ---
    dim_property = df[[
        "id", "room_type", "property_type", "accommodates",
        "bedrooms", "beds", "bathrooms_text", "amenities"
    ]].drop_duplicates(subset=["id"]).reset_index(drop=True)
    dim_property.to_csv(os.path.join(OUT_DIR, "star_schema", "dim_property.csv"), index=False)

    # --- DIM: Review Scores ---
    review_cols = ["id", "review_scores_rating", "review_scores_accuracy",
                   "review_scores_cleanliness", "review_scores_checkin",
                   "review_scores_communication", "review_scores_location",
                   "review_scores_value", "number_of_reviews"]
    existing = [c for c in review_cols if c in df.columns]
    dim_review = df[existing].drop_duplicates(subset=["id"]).reset_index(drop=True)
    dim_review.to_csv(os.path.join(OUT_DIR, "star_schema", "dim_review_scores.csv"), index=False)

    # --- FACT: Listings ---
    location_map = dim_location.set_index("neighbourhood_cleansed")["location_id"]
    fact_listings = df[[
        "id", "host_id", "neighbourhood_cleansed", "price",
        "minimum_nights", "maximum_nights", "availability_365",
        "occupancy_rate", "estimated_annual_revenue", "avg_calendar_price",
        "booked_days", "total_days", "review_frequency",
        "price_per_bedroom", "neighbourhood_median_price"
    ]].copy()
    fact_listings["location_id"] = fact_listings["neighbourhood_cleansed"].map(location_map)
    fact_listings.drop(columns=["neighbourhood_cleansed"], inplace=True)
    fact_listings.to_csv(os.path.join(OUT_DIR, "star_schema", "fact_listings.csv"), index=False)

    log.info("Star schema tables saved.")
    log.info(f"  dim_host: {len(dim_host)} rows")
    log.info(f"  dim_location: {len(dim_location)} rows")
    log.info(f"  dim_property: {len(dim_property)} rows")
    log.info(f"  fact_listings: {len(fact_listings)} rows")


def run():
    build_enriched_listings()
    build_star_schema()

if __name__ == "__main__":
    run()