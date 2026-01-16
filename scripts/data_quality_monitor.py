"""
Data Quality Monitoring Script
Automated checks for data freshness, anomalies, and business logic validation
"""
import duckdb
from datetime import datetime, timedelta
import json

class DataQualityMonitor:
    def __init__(self, db_path='ecommerce_analytics.duckdb'):
        import os
        
        # Validate database exists
        if not os.path.exists(db_path):
            raise FileNotFoundError(
                f"Database not found at '{db_path}'. "
                f"Make sure to run 'dbt run' first from the ecommerce_analytics/ directory. "
                f"Current directory: {os.getcwd()}"
            )
        
        self.conn = duckdb.connect(db_path, read_only=True)
        self.checks_passed = 0
        self.checks_failed = 0
        self.alerts = []
    
    def run_all_checks(self):
        """Run all data quality checks"""
        print("=" * 60)
        print("DATA QUALITY MONITORING REPORT")
        print(f"Generated at: {datetime.now()}")
        print("=" * 60)
        
        self.check_data_completeness()
        self.check_anomalies()
        self.check_null_rates()
        self.check_revenue_reconciliation()
        self.check_tax_coverage()
        
        self.print_summary()
        return self.generate_report()
    
    def check_data_completeness(self):
        """Check if we have sufficient data for analysis"""
        query = """
        SELECT 
            min(order_date) as earliest_order_date,
            max(order_date) as latest_order_date,
            count(distinct order_date) as days_with_data,
            count(*) as total_orders
        FROM main_marts.fct_revenue_daily
        """
        try:
            result = self.conn.execute(query).fetchone()
            earliest, latest, days_count, total_orders = result
            
            # Check if we have reasonable amount of data
            if total_orders < 100:
                self.log_failure(f"⚠️  Data Completeness: Only {total_orders} order records found (expected >100)")
            elif days_count < 30:
                self.log_failure(f"⚠️  Data Completeness: Only {days_count} days of data (expected >30)")
            else:
                self.log_success(f"✅ Data Completeness: {total_orders} orders across {days_count} days ({earliest} to {latest})")
        except Exception as e:
            self.log_failure(f"⚠️  Data Completeness: Check failed - {str(e)}")
    
    def check_anomalies(self):
        """Detect anomalies in daily revenue - with relaxed threshold for sample data"""
        query = """
        WITH daily_stats AS (
            SELECT 
                order_date,
                sum(total_orders) as daily_orders,
                AVG(sum(total_orders)) OVER (
                    ORDER BY order_date 
                    ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
                ) as avg_orders_7d
            FROM main_marts.fct_revenue_daily
            GROUP BY order_date
            HAVING count(*) > 0
        ),
        anomalies AS (
            SELECT 
                order_date,
                daily_orders,
                avg_orders_7d,
                CASE 
                    WHEN avg_orders_7d > 0 AND daily_orders < avg_orders_7d * 0.2 THEN 'severe_drop'
                    WHEN avg_orders_7d > 0 AND daily_orders > avg_orders_7d * 5.0 THEN 'severe_spike'
                    ELSE 'normal'
                END as anomaly_type
            FROM daily_stats
            WHERE avg_orders_7d > 0
        )
        SELECT 
            COUNT(*) as total_days,
            SUM(CASE WHEN anomaly_type != 'normal' THEN 1 ELSE 0 END) as anomaly_count
        FROM anomalies
        """
        try:
            result = self.conn.execute(query).fetchone()
            total_days, anomaly_count = result
            
            # More lenient threshold - allow up to 10% anomaly rate for random sample data
            anomaly_rate = (anomaly_count / total_days * 100) if total_days > 0 else 0
            
            if anomaly_rate > 10:
                self.log_failure(f"⚠️  Anomaly Detection: {anomaly_count}/{total_days} days with severe anomalies ({anomaly_rate:.1f}%)")
            else:
                self.log_success(f"✅ Anomaly Detection: {anomaly_count}/{total_days} days with anomalies ({anomaly_rate:.1f}% - within acceptable range)")
        except Exception as e:
            self.log_failure(f"⚠️  Anomaly Detection: Check failed - {str(e)}")
    
    def check_null_rates(self):
        """Check for unexpected null values"""
        query = """
        SELECT 
            COUNT(*) as total_orders,
            SUM(CASE WHEN destination_country IS NULL THEN 1 ELSE 0 END) as null_country,
            SUM(CASE WHEN channel IS NULL THEN 1 ELSE 0 END) as null_channel
        FROM main_staging.stg_orders
        """
        try:
            result = self.conn.execute(query).fetchone()
            total, null_country, null_channel = result
            
            if total == 0:
                self.log_failure("⚠️  Null Rate Check: No data found in staging.stg_orders")
                return
            
            null_rate = ((null_country + null_channel) / (total * 2)) * 100
            
            if null_rate > 1:
                self.log_failure(f"⚠️  Null Rate Check: {null_rate:.2f}% null rate in critical fields")
            else:
                self.log_success(f"✅ Null Rate Check: {null_rate:.2f}% null rate (acceptable)")
        except Exception as e:
            self.log_failure(f"⚠️  Null Rate Check: Check failed - {str(e)}")
    
    def check_revenue_reconciliation(self):
        """Verify revenue calculations are consistent"""
        query = """
        SELECT 
            SUM(total_gross_revenue) as gross_from_daily,
            (SELECT SUM(gross_revenue) FROM main_intermediate.int_order_revenue) as gross_from_orders,
            ABS(SUM(total_gross_revenue) - (SELECT SUM(gross_revenue) FROM main_intermediate.int_order_revenue)) as difference
        FROM main_marts.fct_revenue_daily
        """
        try:
            result = self.conn.execute(query).fetchone()
            daily_sum, order_sum, difference = result
            
            if daily_sum is None or order_sum is None:
                self.log_failure("⚠️  Revenue Reconciliation: Missing revenue data")
                return
            
            # Allow small rounding differences (up to $1)
            if difference > 1.00:
                self.log_failure(f"⚠️  Revenue Reconciliation: ${difference:.2f} mismatch between aggregations")
            else:
                self.log_success(f"✅ Revenue Reconciliation: Revenue matches (difference: ${difference:.2f})")
        except Exception as e:
            self.log_failure(f"⚠️  Revenue Reconciliation: Check failed - {str(e)}")
    
    def check_tax_coverage(self):
        """Ensure completed orders have appropriate tax records"""
        query = """
        WITH order_tax_summary AS (
            SELECT 
                o.order_id,
                o.order_status,
                o.destination_country,
                COUNT(DISTINCT t.tax_transaction_id) as tax_record_count,
                SUM(CASE WHEN t.tax_type = 'VAT' THEN 1 ELSE 0 END) as has_vat,
                SUM(CASE WHEN t.tax_type = 'DUTY' THEN 1 ELSE 0 END) as has_duty
            FROM main_staging.stg_orders o
            LEFT JOIN main_staging.stg_tax_transactions t ON o.order_id = t.order_id
            WHERE o.order_status = 'completed'
            GROUP BY o.order_id, o.order_status, o.destination_country
        )
        SELECT 
            COUNT(*) as completed_orders,
            SUM(CASE WHEN tax_record_count = 0 THEN 1 ELSE 0 END) as orders_without_tax,
            SUM(CASE WHEN has_vat = 0 THEN 1 ELSE 0 END) as orders_without_vat
        FROM order_tax_summary
        """
        try:
            result = self.conn.execute(query).fetchone()
            completed, without_tax, without_vat = result
            
            if completed == 0:
                self.log_failure("⚠️  Tax Coverage: No completed orders found")
                return
            
            if without_tax > 0:
                self.log_failure(f"⚠️  Tax Coverage: {without_tax}/{completed} completed orders missing all tax records")
            elif without_vat > 0:
                self.log_failure(f"⚠️  Tax Coverage: {without_vat}/{completed} completed orders missing VAT")
            else:
                self.log_success(f"✅ Tax Coverage: All {completed} completed orders have appropriate tax records")
        except Exception as e:
            self.log_failure(f"⚠️  Tax Coverage: Check failed - {str(e)}")
    
    def log_success(self, message):
        print(f"\n{message}")
        self.checks_passed += 1
    
    def log_failure(self, message):
        print(f"\n{message}")
        self.checks_failed += 1
        self.alerts.append(message)
    
    def print_summary(self):
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"✅ Checks Passed: {self.checks_passed}")
        print(f"❌ Checks Failed: {self.checks_failed}")
        
        if self.checks_failed == 0:
            print("\n🎉 All data quality checks passed!")
        elif self.alerts:
            print("\n🚨 ALERTS REQUIRING ATTENTION:")
            for alert in self.alerts:
                print(f"  - {alert}")
    
    def generate_report(self):
        return {
            'timestamp': datetime.now().isoformat(),
            'checks_passed': self.checks_passed,
            'checks_failed': self.checks_failed,
            'alerts': self.alerts,
            'status': 'PASSED' if self.checks_failed == 0 else 'FAILED'
        }

if __name__ == "__main__":
    monitor = DataQualityMonitor()
    report = monitor.run_all_checks()
    
    # Save report
    with open('data_quality_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n📊 Report saved to: data_quality_report.json")
    
    # Exit with appropriate code for CI/CD integration
    exit(0 if report['status'] == 'PASSED' else 1)