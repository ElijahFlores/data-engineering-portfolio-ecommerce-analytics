"""
Sample Data Generator for Cross-Border E-commerce Analytics
Generates realistic transaction data across multiple sales channels
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Generate date range (90 days)
start_date = datetime(2024, 10, 1)
dates = [start_date + timedelta(days=x) for x in range(90)]

# 1. ORDERS TABLE
print("Generating orders data...")
orders_data = []
order_id = 1000

for _ in range(500):
    order_date = random.choice(dates)
    channel = random.choices(
        ['dtc_website', 'tiktok_shop', 'amazon'],
        weights=[0.4, 0.35, 0.25]
    )[0]
    
    destination_country = random.choices(
        ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'JP'],
        weights=[0.3, 0.2, 0.15, 0.1, 0.1, 0.08, 0.07]
    )[0]
    
    currency = {
        'US': 'USD', 'UK': 'GBP', 'CA': 'CAD',
        'AU': 'AUD', 'DE': 'EUR', 'FR': 'EUR', 'JP': 'JPY'
    }[destination_country]
    
    # Order amounts
    gross_sale = round(random.uniform(50, 500), 2)
    discount = round(gross_sale * random.choice([0, 0.1, 0.15, 0.2]), 2)
    shipping_fee = round(random.uniform(5, 25), 2)
    
    # Channel fees
    channel_fee_rate = {'dtc_website': 0.029, 'tiktok_shop': 0.08, 'amazon': 0.15}
    channel_fee = round((gross_sale - discount) * channel_fee_rate[channel], 2)
    
    orders_data.append({
        'order_id': f'ORD-{order_id}',
        'order_date': order_date.strftime('%Y-%m-%d'),
        'channel': channel,
        'destination_country': destination_country,
        'currency': currency,
        'gross_sale_amount': gross_sale,
        'discount_amount': discount,
        'shipping_fee': shipping_fee,
        'channel_fee': channel_fee,
        'order_status': random.choices(
            ['completed', 'refunded', 'cancelled'],
            weights=[0.85, 0.1, 0.05]
        )[0]
    })
    order_id += 1

orders_df = pd.DataFrame(orders_data)

# 2. TAX TRANSACTIONS TABLE
print("Generating tax transactions...")
tax_data = []
for _, order in orders_df.iterrows():
    if order['order_status'] != 'cancelled':
        net_sale = order['gross_sale_amount'] - order['discount_amount']
        
        # Tax rates by country
        tax_rates = {
            'US': 0.08, 'UK': 0.20, 'CA': 0.13,
            'AU': 0.10, 'DE': 0.19, 'FR': 0.20, 'JP': 0.10
        }
        
        vat_amount = round(net_sale * tax_rates[order['destination_country']], 2)
        
        tax_data.append({
            'tax_transaction_id': f'TAX-{order["order_id"]}',
            'order_id': order['order_id'],
            'transaction_date': order['order_date'],
            'destination_country': order['destination_country'],
            'tax_type': 'VAT',
            'taxable_amount': net_sale,
            'tax_rate': tax_rates[order['destination_country']],
            'tax_amount': vat_amount,
            'currency': order['currency']
        })
        
        # Import duties (international orders only, not US domestic)
        if order['destination_country'] != 'US':
            duty_rate = random.choice([0, 0.05, 0.08, 0.12])
            if duty_rate > 0:
                duty_amount = round(net_sale * duty_rate, 2)
                tax_data.append({
                    'tax_transaction_id': f'DUTY-{order["order_id"]}',
                    'order_id': order['order_id'],
                    'transaction_date': order['order_date'],
                    'destination_country': order['destination_country'],
                    'tax_type': 'DUTY',
                    'taxable_amount': net_sale,
                    'tax_rate': duty_rate,
                    'tax_amount': duty_amount,
                    'currency': order['currency']
                })

tax_df = pd.DataFrame(tax_data)

# 3. FULFILLMENT COSTS TABLE
print("Generating fulfillment costs...")
fulfillment_data = []
for _, order in orders_df.iterrows():
    if order['order_status'] == 'completed':
        # Warehouse picking/packing
        picking_cost = round(random.uniform(2, 5), 2)
        
        # International shipping cost (higher than customer-paid shipping)
        base_shipping = order['shipping_fee']
        actual_shipping = round(base_shipping * random.uniform(1.5, 2.5), 2)
        
        # Customs clearance for international
        customs_cost = round(random.uniform(5, 15), 2) if order['destination_country'] != 'US' else 0
        
        fulfillment_data.append({
            'fulfillment_id': f'FUL-{order["order_id"]}',
            'order_id': order['order_id'],
            'fulfillment_date': (pd.to_datetime(order['order_date']) + timedelta(days=random.randint(1, 3))).strftime('%Y-%m-%d'),
            'warehouse_cost': picking_cost,
            'shipping_cost': actual_shipping,
            'customs_clearance_cost': customs_cost,
            'total_fulfillment_cost': picking_cost + actual_shipping + customs_cost
        })

fulfillment_df = pd.DataFrame(fulfillment_data)

# 4. REFUNDS TABLE
print("Generating refunds...")
refund_data = []
refund_id = 2000
for _, order in orders_df[orders_df['order_status'] == 'refunded'].iterrows():
    # Refund includes gross sale minus discount, plus shipping
    refund_amount = order['gross_sale_amount'] - order['discount_amount'] + order['shipping_fee']
    
    refund_data.append({
        'refund_id': f'REF-{refund_id}',
        'order_id': order['order_id'],
        'refund_date': (pd.to_datetime(order['order_date']) + timedelta(days=random.randint(5, 30))).strftime('%Y-%m-%d'),
        'refund_amount': refund_amount,
        'refund_reason': random.choice([
            'customer_request', 'damaged_product', 'wrong_item', 'quality_issue'
        ]),
        'currency': order['currency']
    })
    refund_id += 1

refunds_df = pd.DataFrame(refund_data)

# Save to CSV files
print("\nSaving CSV files...")
orders_df.to_csv('data/raw/orders.csv', index=False)
tax_df.to_csv('data/raw/tax_transactions.csv', index=False)
fulfillment_df.to_csv('data/raw/fulfillment_costs.csv', index=False)
refunds_df.to_csv('data/raw/refunds.csv', index=False)

print("\n✅ Sample data generated successfully!")
print(f"\nData Summary:")
print(f"  Orders: {len(orders_df)} records")
print(f"  Tax Transactions: {len(tax_df)} records")
print(f"  Fulfillment Records: {len(fulfillment_df)} records")
print(f"  Refunds: {len(refunds_df)} records")
print(f"\n📁 Files created in data/raw/:")
print("  - orders.csv")
print("  - tax_transactions.csv")
print("  - fulfillment_costs.csv")
print("  - refunds.csv")
