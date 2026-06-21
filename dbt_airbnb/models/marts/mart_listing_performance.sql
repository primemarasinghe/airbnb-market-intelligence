-- Mart: comprehensive listing performance table
-- Joins all dimensions with fact for analytical queries

with listings as (
    select * from {{ ref('stg_listings') }}
),

hosts as (
    select * from {{ ref('stg_hosts') }}
),

locations as (
    select * from {{ ref('stg_locations') }}
),

reviews as (
    select * from dim_review_scores
),

final as (
    select
        -- Listing identifiers
        l.listing_id,
        l.host_id,
        l.location_id,

        -- Pricing
        l.price,
        l.price_tier,
        l.price_per_bedroom,
        l.neighbourhood_median_price,
        round(l.price / nullif(l.neighbourhood_median_price, 0), 2) as price_vs_median_ratio,

        -- Availability & Occupancy
        l.availability_365,
        l.occupancy_rate,
        l.occupancy_tier,
        l.booked_days,
        l.estimated_annual_revenue,

        -- Host attributes
        h.host_name,
        h.host_type,
        h.host_experience_tier,
        h.host_is_superhost,
        h.host_tenure_years,
        h.host_listing_count_actual,
        h.host_response_rate,

        -- Location attributes
        loc.neighbourhood,
        loc.neighbourhood_price_zone,
        loc.neighbourhood_listing_count,
        loc.neighbourhood_avg_rating,

        -- Review scores
        r.review_scores_rating,
        r.review_scores_cleanliness,
        r.review_scores_location,
        r.review_scores_communication,
        r.review_scores_value,
        r.number_of_reviews

    from listings l
    left join hosts h on l.host_id = h.host_id
    left join locations loc on l.location_id = loc.location_id
    left join reviews r on l.listing_id = r.id
)

select * from final