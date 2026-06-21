-- Test: all listing prices must be positive
select listing_id, price
from {{ ref('stg_listings') }}
where price <= 0