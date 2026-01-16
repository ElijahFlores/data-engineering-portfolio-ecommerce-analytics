# Cross-Border E-commerce Analytics Platform

## 🎯 Project Overview

An end-to-end analytics engineering project demonstrating production-ready data pipelines for cross-border e-commerce operations. This project models revenue, taxes, and profitability across multiple sales channels (DTC website, TikTok Shop, Amazon) with robust data quality monitoring.

**Portfolio Project for Analytics Engineer Role**

## 🏗️ Architecture

```
Raw Data (CSV Files)
    ↓
DuckDB (Data Warehouse)
    ↓
dbt (Transformation Layer)
    ├── Staging Models (data cleaning & validation)
    ├── Intermediate Models (business logic)
    └── Mart Models (business-ready analytics tables)
    ↓
Data Quality Monitoring (Python + dbt tests)
    ↓
Business Insights (SQL queries)
```

## 📊 Data Models

### Staging Layer (`models/staging/`)
- **stg_orders**: Cleaned order data from all sales channels
- **stg_tax_transactions**: VAT and duty tax records
- **stg_fulfillment_costs**: Warehouse and logistics costs
- **stg_refunds**: Customer refund transactions

### Intermediate Layer (`models/intermediate/`)
- **int_order_revenue**: Comprehensive revenue calculation including:
  - Gross revenue (sales + shipping)
  - Net revenue (after channel fees, taxes, fulfillment costs)
  - Margin percentage
  - Refund impact modeling

### Mart Layer (`models/marts/`)
- **fct_revenue_daily**: Daily revenue metrics by channel and country
- **fct_tax_filing_summary**: Monthly tax compliance reporting by jurisdiction

## 🔑 Key Features

### 1. Business-Critical Revenue Pipeline
**Net Revenue Formula:**
```
Net Revenue = Gross Sales + Shipping Revenue 
              - Discounts 
              - Channel Fees 
              - Taxes (VAT + Duties)
              - Fulfillment Costs
```

Handles:
- Multi-channel reconciliation (DTC, TikTok Shop, Amazon)
- Refund accounting (reverses all components)
- Margin and profitability analysis

### 2. Tax Compliance Pipeline
- VAT tracking by destination country
- Import duty calculations for cross-border orders
- Monthly tax filing summaries for audit trails
- Supports multiple currencies

### 3. Data Quality Framework

**Three-Layer Testing Approach:**

1. **dbt Schema Tests** (automated)
   - Uniqueness constraints
   - Not-null validation
   - Referential integrity
   - Accepted value ranges

2. **Custom SQL Tests** (business logic)
   - Revenue reconciliation checks
   - Cross-table validation

3. **Python Monitoring** (operational)
   - Data freshness alerts
   - Anomaly detection
   - Null rate monitoring
   - Tax coverage verification

### 4. Software Engineering Best Practices
- ✅ Version control ready (Git)
- ✅ Modular SQL with dbt ref() functions
- ✅ Comprehensive inline documentation
- ✅ Automated testing (15+ tests)
- ✅ Clear naming conventions
- ✅ Separation of concerns (staging → intermediate → marts)

## 🚀 Quick Start

### Prerequisites
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Setup & Run
```bash
# 1. Generate sample data
python generate_sample_data.py

# 2. Install dbt packages
cd ecommerce_analytics
dbt deps

# 3. Run dbt models
dbt run

# 4. Run tests
dbt test

# 5. Run data quality monitoring
cd ..
python scripts/data_quality_monitor.py

# 6. View documentation
cd ecommerce_analytics
dbt docs generate
dbt docs serve  # Opens in browser at localhost:8080
```

## 📈 Sample Business Insights

### Revenue Analysis
```sql
-- Net revenue trend by channel
SELECT 
    order_date,
    channel,
    SUM(total_net_revenue) as net_revenue,
    AVG(avg_margin_percentage) as avg_margin
FROM marts.fct_revenue_daily
GROUP BY order_date, channel
ORDER BY order_date DESC;
```

### Tax Reporting
```sql
-- Monthly tax liability by country
SELECT 
    tax_month,
    destination_country,
    tax_type,
    SUM(total_tax_collected) as tax_liability
FROM marts.fct_tax_filing_summary
GROUP BY tax_month, destination_country, tax_type
ORDER BY tax_month DESC, tax_liability DESC;
```

### Profitability Analysis
```sql
-- Channel profitability comparison
SELECT 
    channel,
    SUM(total_gross_revenue) as gross_revenue,
    SUM(total_net_revenue) as net_revenue,
    SUM(total_channel_fees) as platform_fees,
    SUM(total_fulfillment_cost) as logistics_cost,
    ROUND(SUM(total_net_revenue) / SUM(total_gross_revenue) * 100, 2) as net_margin_pct
FROM marts.fct_revenue_daily
GROUP BY channel;
```

## 🧪 Data Quality Results

**Example Test Results:**
```
✅ All 15 dbt schema tests passed
✅ Revenue reconciliation: 100% accuracy
✅ Tax coverage: All completed orders have VAT records
✅ Data freshness: Updated within last 24 hours
✅ Null rate: 0.00% in critical fields
```

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Database** | DuckDB | Local analytics database (Snowflake-compatible SQL) |
| **Transformation** | dbt Core | SQL-based data modeling & testing |
| **Testing** | dbt tests + Python | Comprehensive data quality assurance |
| **Orchestration** | Python | Pipeline automation & monitoring |
| **Documentation** | dbt docs | Auto-generated data catalog with lineage |
| **Version Control** | Git | Code management & collaboration |

## 📚 Skills Demonstrated

### Technical Skills
- ✅ **Advanced SQL**: CTEs, window functions, complex joins, aggregations
- ✅ **dbt Expertise**: Modular models, testing, documentation, Jinja templating
- ✅ **Data Modeling**: Dimensional modeling, fact/dimension tables, slowly changing dimensions
- ✅ **Python**: Automation, data quality monitoring, error handling
- ✅ **Version Control**: Git workflow, code organization

### Analytics Engineering Skills
- ✅ **Business-Critical Pipelines**: Revenue recognition, tax compliance
- ✅ **Data Quality**: Multi-layer testing strategy, monitoring, alerting
- ✅ **Documentation**: Clear README, inline comments, dbt docs
- ✅ **Production Mindset**: Error handling, edge cases, audit trails

### Business Acumen
- ✅ **E-commerce Domain**: Multi-channel operations, cross-border complexity
- ✅ **Financial Reporting**: Revenue accounting, margin analysis
- ✅ **Tax & Compliance**: VAT/duty calculations, audit readiness
- ✅ **Stakeholder Communication**: Clear documentation, business metrics

## 📂 Project Structure

```
ecommerce-analytics-portfolio/
├── data/
│   └── raw/                     # Sample CSV files
├── ecommerce_analytics/         # dbt project
│   ├── models/
│   │   ├── staging/            # Source data cleaning
│   │   ├── intermediate/       # Business logic
│   │   └── marts/              # Analytics-ready tables
│   ├── tests/                  # Custom SQL tests
│   ├── dbt_project.yml
│   ├── packages.yml
│   └── profiles.yml
├── scripts/
│   └── data_quality_monitor.py # Automated monitoring
├── generate_sample_data.py     # Data generation
├── requirements.txt
└── README.md
```

## 🎓 Learning Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [DuckDB SQL Reference](https://duckdb.org/docs/sql/introduction)
- [Analytics Engineering Guide](https://www.getdbt.com/analytics-engineering/)
- [Dimensional Modeling](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)


**Project Stats:**
- ⏱️ Completion Time: ~3 hours
- 💻 Code: ~600 lines SQL + 250 lines Python
- ✅ Test Coverage: 15+ data quality tests
- 📊 Data Models: 9 models across 3 layers