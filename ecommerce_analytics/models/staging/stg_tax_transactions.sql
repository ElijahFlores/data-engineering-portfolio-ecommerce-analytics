{{
    config(
        materialized='view',
        tags=['staging', 'tax']
    )
}}

with source_data as (
    select * from read_csv_auto('../data/raw/tax_transactions.csv')
),

cleaned as (
    select
        tax_transaction_id,
        order_id,
        cast(transaction_date as date) as transaction_date,
        destination_country,
        tax_type,
        taxable_amount,
        tax_rate,
        tax_amount,
        currency,
        
        -- Audit fields
        current_timestamp as dbt_loaded_at
        
    from source_data
    where tax_transaction_id is not null
)

select * from cleaned
