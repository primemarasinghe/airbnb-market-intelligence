import pytest
import pandas as pd
import numpy as np
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Test Data Ingestion ---
class TestIngestion:
    def test_raw_files_exist(self):
        raw_dir = "data/raw/Bangkok/data"
        assert os.path.exists(raw_dir), "Raw data directory missing"
        assert os.path.exists(f"{raw_dir}/listings.csv"), "listings.csv missing"
        assert os.path.exists(f"{raw_dir}/calendar.csv"), "calendar.csv missing"
        assert os.path.exists(f"{raw_dir}/reviews.csv"), "reviews.csv missing"

    def test_metadata_exists(self):
        meta_path = "data/raw/Bangkok/ingest_metadata.json"
        assert os.path.exists(meta_path), "Metadata file missing"

# --- Test Cleaned Data ---
class TestCleaning:
    @pytest.fixture
    def listings(self):
        return pd.read_csv("data/processed/listings_clean.csv", low_memory=False)

    def test_listings_not_empty(self, listings):
        assert len(listings) > 0, "Listings is empty"

    def test_no_duplicate_ids(self, listings):
        assert listings["id"].duplicated().sum() == 0, "Duplicate listing IDs found"

    def test_price_is_numeric(self, listings):
        assert pd.api.types.is_float_dtype(listings["price"]), "Price not numeric"

    def test_no_negative_prices(self, listings):
        valid_prices = listings["price"].dropna()
        assert (valid_prices >= 0).all(), "Negative prices found"

    def test_valid_coordinates(self, listings):
        valid_lat = listings["latitude"].between(12, 16)
        valid_lon = listings["longitude"].between(99, 102)
        invalid = (~valid_lat | ~valid_lon).sum()
        assert invalid < 100, f"Too many invalid coordinates: {invalid}"

    def test_room_type_values(self, listings):
        valid_types = {"Entire Home/Apt", "Private Room", "Shared Room", "Hotel Room"}
        actual = set(listings["room_type"].dropna().unique())
        assert actual.issubset(valid_types), f"Unexpected room types: {actual - valid_types}"

    def test_boolean_fields(self, listings):
        for col in ["host_is_superhost", "instant_bookable"]:
            if col in listings.columns:
                unique_vals = set(listings[col].dropna().unique())
                assert unique_vals.issubset({True, False, 1.0, 0.0}), \
                    f"{col} has unexpected values: {unique_vals}"

# --- Test Enriched Data ---
class TestEnrichment:
    @pytest.fixture
    def enriched(self):
        return pd.read_csv("data/processed/listings_enriched.csv", low_memory=False)

    def test_enriched_has_more_columns(self, enriched):
        assert len(enriched.columns) > 79, "Enriched should have more columns than raw"

    def test_neighbourhood_aggregates_exist(self, enriched):
        assert "neighbourhood_median_price" in enriched.columns
        assert "neighbourhood_listing_count" in enriched.columns

    def test_host_type_values(self, enriched):
        valid = {"Single", "Small Multi", "Commercial"}
        actual = set(enriched["host_type"].dropna().unique())
        assert actual.issubset(valid), f"Unexpected host types: {actual}"

    def test_occupancy_rate_range(self, enriched):
        enriched["occupancy_rate"] = 1 - (enriched["availability_365"] / 365)
        valid = enriched["occupancy_rate"].between(0, 1)
        assert valid.all(), "Occupancy rates outside [0,1]"

# --- Test Star Schema ---
class TestStarSchema:
    def test_fact_table_exists(self):
        assert os.path.exists("data/processed/star_schema/fact_listings.csv")

    def test_all_dimensions_exist(self):
        dims = ["dim_host", "dim_location", "dim_property", "dim_review_scores"]
        for dim in dims:
            path = f"data/processed/star_schema/{dim}.csv"
            assert os.path.exists(path), f"{dim}.csv missing"

    def test_fact_listing_count(self):
        fact = pd.read_csv("data/processed/star_schema/fact_listings.csv")
        assert len(fact) == 28806, f"Expected 28806 rows, got {len(fact)}"

    def test_dim_host_unique(self):
        dim = pd.read_csv("data/processed/star_schema/dim_host.csv")
        assert dim["host_id"].duplicated().sum() == 0, "Duplicate host IDs in dim_host"

    def test_dim_location_count(self):
        dim = pd.read_csv("data/processed/star_schema/dim_location.csv")
        assert len(dim) == 50, f"Expected 50 neighbourhoods, got {len(dim)}"

# --- Test Data Quality ---
class TestDataQuality:
    @pytest.fixture
    def listings(self):
        return pd.read_csv("data/processed/listings_clean.csv", low_memory=False)

    def test_critical_fields_completeness(self, listings):
        critical = ["id", "latitude", "longitude", "room_type"]
        for col in critical:
            null_pct = listings[col].isna().mean()
            assert null_pct < 0.01, f"{col} has {null_pct:.1%} nulls — too high"

    def test_price_outlier_flags_exist(self, listings):
        assert "flag_negative_price" in listings.columns
        assert "flag_zero_price" in listings.columns
        assert "flag_invalid_coords" in listings.columns

    def test_listing_count_reasonable(self, listings):
        assert 20000 < len(listings) < 50000, \
            f"Unexpected listing count: {len(listings)}"