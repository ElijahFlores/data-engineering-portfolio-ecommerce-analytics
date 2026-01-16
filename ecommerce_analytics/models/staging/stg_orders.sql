{{
    config(
        materialized='view',
        tags=['staging', 'orders']
    )
}}

with source_data as (
    select * from read_csv_auto('../data/raw/orders.csv')
),

cleaned as (
    select
        order_id,
        cast(order_date as date) as order_date,
        channel,
        destination_country,
        currency,
        gross_sale_amount,
        discount_amount,
        shipping_fee,
        channel_fee,
        order_status,
        
        -- Calculated fields
        gross_sale_amount - discount_amount as net_sale_amount,
        
        -- Data quality flags
        case 
            when gross_sale_amount < 0 then 1 
            else 0 
        end as has_negative_amount_flag,
        
        current_timestamp as dbt_loaded_at
        
    from source_data
    where order_id is not null
)

select * from cleaned
