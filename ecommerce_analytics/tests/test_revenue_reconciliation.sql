-- Test that net revenue calculation is consistent for completed orders
-- Failure indicates data quality issue in revenue pipeline

with revenue_check as (
    select
        order_id,
        net_revenue,
        gross_revenue,
        channel_fee,
        total_tax_amount,
        fulfillment_cost,
        order_status,
        
        -- Recalculate net revenue for completed orders
        (gross_revenue - channel_fee - total_tax_amount - fulfillment_cost) as calculated_net_revenue,
        
        -- Check if they match (allow small rounding differences)
        abs(net_revenue - (gross_revenue - channel_fee - total_tax_amount - fulfillment_cost)) as revenue_difference
        
    from {{ ref('int_order_revenue') }}
    where order_status = 'completed'
)

-- Return rows that fail the test (difference exceeds 2 cents)
select *
from revenue_check
where revenue_difference > 0.02
