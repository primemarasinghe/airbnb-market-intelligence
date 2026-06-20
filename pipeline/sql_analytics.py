import duckdb
import pandas as pd
import os

os.makedirs("data/processed/duckdb", exist_ok=True)

con = duckdb.connect("data/processed/duckdb/airbnb.db")

# Load star schema tables
con.execute("""
    CREATE OR REPLACE TABLE fact_listings AS 
    SELECT * FROM read_csv_auto('data/processed/star_schema/fact_listings.csv')
""")
con.execute("""
    CREATE OR REPLACE TABLE dim_host AS 
    SELECT * FROM read_csv_auto('data/processed/star_schema/dim_host.csv')
""")
con.execute("""
    CREATE OR REPLACE TABLE dim_location AS 
    SELECT * FROM read_csv_auto('data/processed/star_schema/dim_location.csv')
""")
con.execute("""
    CREATE OR REPLACE TABLE dim_property AS 
    SELECT * FROM read_csv_auto('data/processed/star_schema/dim_property.csv')
""")
con.execute("""
    CREATE OR REPLACE TABLE dim_review_scores AS 
    SELECT * FROM read_csv_auto('data/processed/star_schema/dim_review_scores.csv')
""")

print("Tables loaded into DuckDB")

con.execute("""
    CREATE OR REPLACE TABLE fact_listings AS 
    SELECT *,
        ROUND(price * occupancy_rate * 365, 0) AS computed_revenue
    FROM fact_listings
""")

# --- Query 1: Top 10 neighbourhoods by median price ---
print("\n--- Q1: Top 10 Neighbourhoods by Median Price ---")
q1 = con.execute("""
    SELECT 
        l.neighbourhood_cleansed,
        COUNT(f.id) as listing_count,
        ROUND(MEDIAN(f.price), 0) as median_price,
        ROUND(AVG(f.occupancy_rate), 3) as avg_occupancy,
        ROUND(AVG(r.review_scores_rating), 3) as avg_rating
    FROM fact_listings f
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_review_scores r ON f.id = r.id
    WHERE f.price BETWEEN 100 AND 10000
    GROUP BY l.neighbourhood_cleansed
    ORDER BY median_price DESC
    LIMIT 10
""").df()
print(q1.to_string())

# --- Query 2: Revenue by host type ---
print("\n--- Q2: Revenue Analysis by Host Type ---")
q2 = con.execute("""
    SELECT 
        h.host_type,
        COUNT(f.id) as listings,
        ROUND(MEDIAN(f.price), 0) as median_price,
        ROUND(AVG(f.occupancy_rate), 3) as avg_occupancy,
        ROUND(MEDIAN(f.computed_revenue), 0) as median_annual_revenue
    FROM fact_listings f
    JOIN dim_host h ON f.host_id = h.host_id
    WHERE f.price BETWEEN 100 AND 10000
    GROUP BY h.host_type
    ORDER BY median_annual_revenue DESC
""").df()
print(q2.to_string())

# --- Query 3: Room type performance ---
print("\n--- Q3: Room Type Performance ---")
q3 = con.execute("""
    SELECT 
        p.room_type,
        COUNT(f.id) as listings,
        ROUND(MEDIAN(f.price), 0) as median_price,
        ROUND(AVG(f.occupancy_rate), 3) as avg_occupancy,
        ROUND(MEDIAN(CAST(f.estimated_annual_revenue AS DOUBLE)), 0) as median_revenue,
        ROUND(AVG(r.review_scores_rating), 3) as avg_rating
    FROM fact_listings f
    JOIN dim_property p ON f.id = p.id
    JOIN dim_review_scores r ON f.id = r.id
    GROUP BY p.room_type
    ORDER BY median_price DESC
""").df()
print(q3.to_string())

# --- Query 4: Superhost vs non-superhost ---
print("\n--- Q4: Superhost Performance Analysis ---")
q4 = con.execute("""
    SELECT 
        h.host_is_superhost,
        COUNT(f.id) as listings,
        ROUND(MEDIAN(f.price), 0) as median_price,
        ROUND(AVG(f.occupancy_rate), 3) as avg_occupancy,
        ROUND(AVG(r.review_scores_rating), 3) as avg_rating,
        ROUND(MEDIAN(f.computed_revenue), 0) as median_revenue
    FROM fact_listings f
    JOIN dim_host h ON f.host_id = h.host_id
    JOIN dim_review_scores r ON f.id = r.id
    GROUP BY h.host_is_superhost
""").df()
print(q4.to_string())

# --- Query 5: Top 10 revenue listings ---
print("\n--- Q5: Top 10 Highest Revenue Listings ---")
q5 = con.execute("""
    SELECT 
        f.id,
        p.room_type,
        l.neighbourhood_cleansed,
        f.price,
        ROUND(f.occupancy_rate, 3) as occupancy_rate,
        ROUND(f.computed_revenue, 0) as annual_revenue
    FROM fact_listings f
    JOIN dim_property p ON f.id = p.id
    JOIN dim_location l ON f.location_id = l.location_id
    WHERE f.price BETWEEN 100 AND 10000
    ORDER BY f.computed_revenue DESC
    LIMIT 10
""").df()
print(q5.to_string())


con.close()
print("\nDuckDB analytics complete.")