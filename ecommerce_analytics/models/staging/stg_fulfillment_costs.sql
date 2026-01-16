{{
    config(
        materialized='view',
        tags=['staging', 'fulfillment']
    )
}}

with source_data as (
    select * from read_csv_auto('../data/raw/fulfillment_costs.csv')
),

cleaned as (
    select
        fulfillment_id,
        order_id,
        cast(fulfillment_date as date) as fulfillment_date,
        warehouse_cost,
        shipping_cost,
        customs_clearance_cost,
        total_fulfillment_cost,
        
        -- Audit fields
        current_timestamp as dbt_loaded_at
        
    from source_data
    where fulfillment_id is not null
)

select * from cleaned
