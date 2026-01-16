{{
    config(
        materialized='table',
        tags=['marts', 'tax', 'compliance']
    )
}}

with tax_transactions as (
    select * from {{ ref('stg_tax_transactions') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

tax_summary as (
    select
        date_trunc('month', t.transaction_date) as tax_month,
        t.destination_country,
        t.tax_type,
        o.channel,
        
        -- Transaction counts
        count(distinct t.tax_transaction_id) as tax_transaction_count,
        count(distinct t.order_id) as unique_order_count,
        
        -- Tax calculations
        sum(t.taxable_amount) as total_taxable_amount,
        round(avg(t.tax_rate), 4) as avg_tax_rate,
        sum(t.tax_amount) as total_tax_collected,
        
        -- Currency tracking
        t.currency,
        
        -- Audit trail
        min(t.transaction_date) as first_transaction_date,
        max(t.transaction_date) as last_transaction_date,
        current_timestamp as report_generated_at
        
    from tax_transactions t
    join orders o on t.order_id = o.order_id
    where o.order_status != 'cancelled'
    group by 
        date_trunc('month', t.transaction_date),
        t.destination_country,
        t.tax_type,
        o.channel,
        t.currency
)

select * from tax_summary
order by tax_month desc, destination_country, tax_type
