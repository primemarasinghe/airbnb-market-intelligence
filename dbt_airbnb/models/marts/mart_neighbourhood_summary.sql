-- Mart: neighbourhood-level market summary for BI dashboards

with performance as (
    select * from {{ ref('mart_listing_performance') }}
),

summary as (
    select
        neighbourhood,
        neighbourhood_price_zone,
        count(listing_id)                           as total_listings,
        round(median(price), 0)                     as median_price,
        round(avg(price), 0)                        as avg_price,
        round(avg(occupancy_rate), 3)               as avg_occupancy_rate,
        round(avg(review_scores_rating), 3)         as avg_rating,
        round(median(estimated_annual_revenue), 0)  as median_annual_revenue,
        count(case when host_is_superhost = true
                   then 1 end)                      as superhost_count,
        round(100.0 * count(case when host_is_superhost = true
                                 then 1 end) / count(*), 1) as superhost_pct,
        round(avg(host_tenure_years), 1)            as avg_host_tenure,
        count(distinct host_id)                     as unique_hosts
    from performance
    where price between 100 and 10000
    group by neighbourhood, neighbourhood_price_zone
)

select * from summary
order by total_listings desc