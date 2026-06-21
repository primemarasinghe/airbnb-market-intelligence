-- Staging model: location dimension

with source as (
    select * from dim_location
),

staged as (
    select
        location_id,
        neighbourhood_cleansed       as neighbourhood,
        neighbourhood_median_price,
        neighbourhood_listing_count,
        neighbourhood_avg_rating,
        -- Price tier classification
        case
            when neighbourhood_median_price >= 2000 then 'Premium Zone'
            when neighbourhood_median_price >= 1400 then 'Mid Zone'
            else 'Budget Zone'
        end as neighbourhood_price_zone
    from source
)

select * from staged