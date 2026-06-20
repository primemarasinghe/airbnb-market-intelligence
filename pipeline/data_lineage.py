import json
from datetime import datetime

lineage = {
    "generated_at": datetime.now().isoformat(),
    "project": "Bangkok Airbnb Market Intelligence",
    "tables": {
        "listings_clean.csv": {
            "source": "data/raw/Bangkok/data/listings.csv",
            "script": "pipeline/clean.py → clean_listings()",
            "transformations": [
                "Price: removed $ symbol, cast to float64",
                "Dates: parsed host_since, last_review to datetime",
                "Booleans: t/f → True/False for superhost, instant_bookable",
                "Percentages: removed % from response_rate, acceptance_rate",
                "Derived: host_tenure_years from host_since to today",
                "Derived: price_per_bedroom = price / bedrooms",
                "Flags: flag_negative_price, flag_zero_price, flag_invalid_coords",
                "Dedup: removed exact duplicates on listing ID"
            ],
            "output_rows": 28806,
            "output_cols": 79
        },
        "calendar_clean.csv": {
            "source": "data/raw/Bangkok/data/calendar.csv",
            "script": "pipeline/clean.py → clean_calendar()",
            "transformations": [
                "Date: parsed to datetime",
                "Available: t/f → True/False",
                "Price: removed $ symbol, cast to float64 (all null in Bangkok)",
                "Derived: day_of_week, month, is_weekend from date"
            ],
            "output_rows": 10514202,
            "output_cols": 10
        },
        "reviews_clean.csv": {
            "source": "data/raw/Bangkok/data/reviews.csv",
            "script": "pipeline/clean.py → clean_reviews()",
            "transformations": [
                "Date: parsed to datetime",
                "Comments: stripped whitespace",
                "Removed exact duplicate rows"
            ],
            "output_rows": 583333,
            "output_cols": 6
        },
        "listings_enriched.csv": {
            "source": "data/processed/listings_clean.csv + calendar_clean.csv",
            "script": "pipeline/enrich.py → build_enriched_listings()",
            "transformations": [
                "Joined neighbourhood aggregates (median_price, listing_count, avg_rating)",
                "Computed occupancy_rate = 1 - (availability_365/365)",
                "Computed estimated_annual_revenue = price × booked_days",
                "Joined avg_calendar_price from calendar (null for Bangkok)",
                "Derived host_listing_count_actual by counting per host_id",
                "Segmented host_type: Single/Small Multi/Commercial",
                "Computed review_frequency = reviews / (tenure_months + 0.01)"
            ],
            "output_rows": 28806,
            "output_cols": 96
        },
        "star_schema/fact_listings.csv": {
            "source": "data/processed/listings_enriched.csv",
            "script": "pipeline/enrich.py → build_star_schema()",
            "transformations": [
                "Selected fact measures: price, occupancy_rate, estimated_annual_revenue",
                "Added location_id FK via neighbourhood_cleansed → dim_location join",
                "Retained host_id FK for dim_host join",
                "Retained listing id FK for dim_property and dim_review_scores"
            ],
            "output_rows": 28806,
            "output_cols": 15
        },
        "star_schema/dim_host.csv": {
            "source": "data/processed/listings_enriched.csv",
            "script": "pipeline/enrich.py → build_star_schema()",
            "transformations": [
                "Deduplicated on host_id (kept first occurrence)",
                "Selected host attributes: name, since, superhost, response_rate",
                "Included derived: host_tenure_years, host_type, host_listing_count_actual"
            ],
            "output_rows": 8874,
            "output_cols": 10
        },
        "star_schema/dim_location.csv": {
            "source": "data/processed/listings_enriched.csv",
            "script": "pipeline/enrich.py → build_star_schema()",
            "transformations": [
                "Deduplicated on neighbourhood_cleansed",
                "Generated surrogate key: location_id",
                "Included neighbourhood aggregates as location attributes"
            ],
            "output_rows": 50,
            "output_cols": 7
        },
        "star_schema/dim_property.csv": {
            "source": "data/processed/listings_enriched.csv",
            "script": "pipeline/enrich.py → build_star_schema()",
            "transformations": [
                "Selected property attributes: room_type, property_type, accommodates",
                "Retained listing id as PK"
            ],
            "output_rows": 28806,
            "output_cols": 8
        },
        "star_schema/dim_review_scores.csv": {
            "source": "data/processed/listings_enriched.csv",
            "script": "pipeline/enrich.py → build_star_schema()",
            "transformations": [
                "Selected review sub-scores: rating, accuracy, cleanliness",
                "checkin, communication, location, value",
                "~35% null (only listings with reviews have scores)"
            ],
            "output_rows": 28806,
            "output_cols": 9
        }
    }
}

with open("data/processed/data_lineage.json", "w") as f:
    json.dump(lineage, f, indent=2)

print("Data lineage document generated.")
for table, info in lineage["tables"].items():
    print(f"\n{table}")
    print(f"  Source: {info['source']}")
    print(f"  Transformations: {len(info['transformations'])}")