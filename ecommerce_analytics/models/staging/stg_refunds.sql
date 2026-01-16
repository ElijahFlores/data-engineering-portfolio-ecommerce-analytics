{{
    config(
        materialized='view',
        tags=['staging', 'refunds']
    )
}}

with source_data as (
    select * from read_csv_auto('../data/raw/refunds.csv')
),

cleaned as (
    select
        refund_id,
        order_id,
        cast(refund_date as date) as refund_date,
        refund_amount,
        refund_reason,
        currency,
        
        -- Audit fields
        current_timestamp as dbt_loaded_at
        
    from source_data
    where refund_id is not null
)

select * from cleaned
