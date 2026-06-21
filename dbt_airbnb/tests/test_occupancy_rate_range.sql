-- Test: occupancy rate must be between 0 and 1
select listing_id, occupancy_rate
from {{ ref('stg_listings') }}
where occupancy_rate < 0 or occupancy_rate > 1