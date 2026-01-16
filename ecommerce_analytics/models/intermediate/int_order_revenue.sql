{{
    config(
        materialized='view',
        tags=['intermediate', 'revenue']
    )
}}

with orders as (
    select * from {{ ref('stg_orders') }}
),

taxes as (
    select
        order_id,
        sum(case when tax_type = 'VAT' then tax_amount else 0 end) as vat_amount,
        sum(case when tax_type = 'DUTY' then tax_amount else 0 end) as duty_amount,
        sum(tax_amount) as total_tax_amount
    from {{ ref('stg_tax_transactions') }}
    group by order_id
),

refunds as (
    select * from {{ ref('stg_refunds') }}
),

fulfillment as (
    select * from {{ ref('stg_fulfillment_costs') }}
),

order_economics as (
    select
        o.order_id,
        o.order_date,
        o.channel,
        o.destination_country,
        o.currency,
        o.order_status,
        
        -- Revenue components
        o.gross_sale_amount,
        o.discount_amount,
        o.net_sale_amount,
        o.shipping_fee as shipping_revenue,
        
        -- Costs
        o.channel_fee,
        coalesce(t.vat_amount, 0) as vat_amount,
        coalesce(t.duty_amount, 0) as duty_amount,
        coalesce(t.total_tax_amount, 0) as total_tax_amount,
        coalesce(f.total_fulfillment_cost, 0) as fulfillment_cost,
        coalesce(r.refund_amount, 0) as refund_amount,
        
        -- Calculate gross revenue (before costs)
        case 
            when o.order_status = 'refunded' then 0
            when o.order_status = 'cancelled' then 0
            else o.net_sale_amount + o.shipping_fee
        end as gross_revenue,
        
        -- Calculate net revenue (after all costs and refunds)
        case 
            when o.order_status = 'refunded' then 
                -1 * (
                    coalesce(r.refund_amount, 0) 
                    + o.channel_fee 
                    + coalesce(t.total_tax_amount, 0)
                    + coalesce(f.total_fulfillment_cost, 0)
                )
            when o.order_status = 'cancelled' then 0
            else (
                o.net_sale_amount 
                + o.shipping_fee
                - o.channel_fee
                - coalesce(t.total_tax_amount, 0)
                - coalesce(f.total_fulfillment_cost, 0)
            )
        end as net_revenue,
        
        -- Margin calculation (only for completed orders)
        case 
            when o.order_status = 'completed' and o.net_sale_amount > 0
            then round(
                ((o.net_sale_amount + o.shipping_fee - o.channel_fee - coalesce(t.total_tax_amount, 0) - coalesce(f.total_fulfillment_cost, 0)) 
                / nullif(o.net_sale_amount + o.shipping_fee, 0)) * 100, 
                2
            )
            else null
        end as margin_percentage
        
    from orders o
    left join taxes t on o.order_id = t.order_id
    left join fulfillment f on o.order_id = f.order_id
    left join refunds r on o.order_id = r.order_id
)

select * from order_economics
