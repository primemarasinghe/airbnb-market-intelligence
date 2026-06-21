-- Staging model: standardize host dimension

with source as (
    select * from dim_host
),

staged as (
    select
        host_id,
        host_name,
        host_since,
        host_is_superhost,
        host_response_rate,
        host_acceptance_rate,
        host_identity_verified,
        host_listing_count_actual,
        host_type,
        host_tenure_years,
        -- Derived
        case
            when host_tenure_years < 1  then 'New Host'
            when host_tenure_years < 3  then 'Established'
            when host_tenure_years < 6  then 'Experienced'
            else 'Veteran'
        end as host_experience_tier,
        case
            when host_is_superhost = true then 1
            else 0
        end as is_superhost_flag
    from source
)

select * from staged