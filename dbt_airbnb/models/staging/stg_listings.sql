-- Staging model: clean and standardize raw listings
-- Source: listings_clean.csv loaded into DuckDB

with source as (
    select * from fact_listings
),

staged as (
    select
        id                          as listing_id,
        host_id,
        location_id,
        price,
        minimum_nights,
        maximum_nights,
        availability_365,
        occupancy_rate,
        estimated_annual_revenue,
        booked_days,
        total_days,
        review_frequency,
        price_per_bedroom,
        neighbourhood_median_price,
        -- Derived fields
        case
            when price < 500  then 'Budget'
            when price < 1500 then 'Mid-Market'
            when price < 3000 then 'Premium'
            else 'Luxury'
        end as price_tier,
        case
            when occupancy_rate >= 0.5 then 'High'
            when occupancy_rate >= 0.25 then 'Medium'
            else 'Low'
        end as occupancy_tier
    from source
    where price > 0
      and price < 50000  -- exclude extreme outliers
)

select * from staged