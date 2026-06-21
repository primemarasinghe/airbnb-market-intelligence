# dbt Airbnb Models

## Project Structure
dbt_airbnb/

├── models/

│   ├── staging/          # Clean and standardize source data

│   │   ├── stg_listings.sql

│   │   ├── stg_hosts.sql

│   │   └── stg_locations.sql

│   └── marts/            # Business-ready analytical tables

│       ├── mart_listing_performance.sql

│       ├── mart_neighbourhood_summary.sql

│       └── mart_host_performance.sql

├── tests/                # Custom data quality tests

├── schema.yml            # Model documentation + built-in tests

└── dbt_project.yml       # Project configuration

## Model Lineage
dim_host ──────────────────────────────┐

dim_location ───────────────────────── mart_listing_performance ──► mart_neighbourhood_summary

fact_listings ──► stg_listings ────────┤                          ──► mart_host_performance

dim_review_scores ─────────────────────┘

## Running Models
```bash
# Install dbt
pip install dbt-core dbt-duckdb

# Run all models
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

## Key Marts
- **mart_listing_performance** — Full listing details with host, location, review scores
- **mart_neighbourhood_summary** — Market overview per neighbourhood for dashboards
- **mart_host_performance** — Host portfolio analytics
