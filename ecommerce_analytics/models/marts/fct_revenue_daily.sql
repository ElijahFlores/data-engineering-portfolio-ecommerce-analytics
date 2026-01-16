{{
    config(
        materialized='table',
        tags=['marts', 'revenue', 'daily']
    )
}}

with order_revenue as (
    select * from {{ ref('int_order_revenue') }}
),

daily_metrics as (
    select
        order_date,
        channel,
        destination_country,
        
        -- Volume metrics
        count(distinct order_id) as total_orders,
        count(distinct case when order_status = 'completed' then order_id end) as completed_orders,
        count(distinct case when order_status = 'refunded' then order_id end) as refunded_orders,
        
        -- Revenue metrics
        sum(gross_revenue) as total_gross_revenue,
        sum(net_revenue) as total_net_revenue,
        
        -- Cost breakdowns
        sum(channel_fee) as total_channel_fees,
        sum(vat_amount) as total_vat,
        sum(duty_amount) as total_duties,
        sum(fulfillment_cost) as total_fulfillment_cost,
        sum(refund_amount) as total_refunds,
        
        -- Performance metrics
        round(avg(case when margin_percentage is not null then margin_percentage end), 2) as avg_margin_percentage,
        round(sum(net_revenue) / nullif(sum(gross_revenue), 0) * 100, 2) as net_margin_percentage
        
    from order_revenue
    group by order_date, channel, destination_country
)

select * from daily_metrics
order by order_date desc, channel, destination_country
