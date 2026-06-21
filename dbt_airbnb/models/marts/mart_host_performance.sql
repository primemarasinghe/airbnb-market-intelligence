-- Mart: host-level performance aggregation

with performance as (
    select * from {{ ref('mart_listing_performance') }}
),

host_summary as (
    select
        host_id,
        host_name,
        host_type,
        host_experience_tier,
        host_is_superhost,
        host_tenure_years,
        host_listing_count_actual,
        host_response_rate,

        count(listing_id)                           as portfolio_size,
        round(avg(price), 0)                        as avg_price,
        round(median(price), 0)                     as median_price,
        round(avg(occupancy_rate), 3)               as avg_occupancy,
        round(sum(estimated_annual_revenue), 0)     as total_portfolio_revenue,
        round(avg(review_scores_rating), 3)         as avg_rating,
        sum(number_of_reviews)                      as total_reviews,
        count(distinct neighbourhood)               as neighbourhoods_active

    from performance
    where price between 100 and 10000
    group by host_id, host_name, host_type, host_experience_tier,
             host_is_superhost, host_tenure_years,
             host_listing_count_actual, host_response_rate
)

select * from host_summary
order by total_portfolio_revenue desc nulls last