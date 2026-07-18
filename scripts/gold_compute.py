"""
RetailPulse - Data Engineering Pipeline
Gold Layer: Analytical Tables & KPIs via SQLite

This script is the final stage of the local data pipeline.
1. It creates a local SQLite database ('database/retail_pulse.db').
2. It loads all cleaned Silver datasets as SQLite tables.
3. It executes optimized SQL queries to calculate target business metrics.
4. It saves the results as Gold tables in 'data/gold/' as CSVs.

By using SQLite, standard Python workflows are integrated with relational SQL 
database systems, which mirrors industry practices.
"""

import os
import sqlite3
import pandas as pd

# Setup paths relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SILVER_DIR = os.path.join(BASE_DIR, "data", "silver")
GOLD_DIR = os.path.join(BASE_DIR, "data", "gold")
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "retail_pulse.db")

def load_silver_to_sqlite(conn):
    """Loads all five silver CSV files into SQLite database tables."""
    print("Loading cleaned Silver datasets into SQLite...")
    
    files = {
        "orders_clean.csv": "orders",
        "inventory_clean.csv": "inventory",
        "products_clean.csv": "products",
        "stores_clean.csv": "stores",
        "suppliers_clean.csv": "suppliers"
    }
    
    for filename, table_name in files.items():
        csv_path = os.path.join(SILVER_DIR, filename)
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Missing silver file: {filename}. Please run silver cleaning first.")
        
        # Read cleaned csv
        df = pd.read_csv(csv_path)
        
        # Load into SQLite database, overwrite if exists
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"  [DB] Loaded table '{table_name}' with {len(df)} rows.")

def compute_kpis(conn):
    """Computes the 4 KPIs using standard SQL queries on the SQLite tables."""
    print("\nComputing business KPIs using SQLite SQL engines...")
    
    # ----------------------------------------------------
    # KPI 1: Low Stock Alerts
    # ----------------------------------------------------
    print("Running SQL for Low Stock Alerts...")
    low_stock_sql = """
        SELECT 
            p.product_name,
            s.store_name,
            i.stock_level,
            i.reorder_level,
            (i.reorder_level - i.stock_level) AS units_needed,
            p.category,
            s.city,
            sup.supplier_name,
            sup.lead_time_days
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        JOIN stores s ON i.store_id = s.store_id
        JOIN suppliers sup ON p.supplier_id = sup.supplier_id
        WHERE i.stock_level < i.reorder_level
        ORDER BY units_needed DESC
    """
    df_low_stock = pd.read_sql_query(low_stock_sql, conn)
    low_stock_path = os.path.join(GOLD_DIR, "low_stock_alerts.csv")
    df_low_stock.to_csv(low_stock_path, index=False)
    print(f"  [OK] Saved {len(df_low_stock)} stockout alerts to: {low_stock_path}")
    
    # ----------------------------------------------------
    # KPI 2: Daily Sales Report
    # ----------------------------------------------------
    print("Running SQL for Daily Sales Trends...")
    daily_sales_sql = """
        SELECT 
            order_date AS date,
            COUNT(order_id) AS total_orders,
            ROUND(SUM(total_amount), 2) AS total_revenue,
            ROUND(AVG(total_amount), 2) AS avg_order_val
        FROM orders
        GROUP BY order_date
        ORDER BY order_date ASC
    """
    df_daily_sales = pd.read_sql_query(daily_sales_sql, conn)
    daily_sales_path = os.path.join(GOLD_DIR, "daily_sales.csv")
    df_daily_sales.to_csv(daily_sales_path, index=False)
    print(f"  [OK] Saved {len(df_daily_sales)} days of sales records to: {daily_sales_path}")

    # ----------------------------------------------------
    # KPI 3: Top Selling Products
    # ----------------------------------------------------
    print("Running SQL for Top 10 Products by Revenue...")
    top_products_sql = """
        SELECT 
            p.product_name,
            p.category,
            ROUND(SUM(o.total_amount), 2) AS total_revenue,
            SUM(o.quantity) AS units_sold
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY total_revenue DESC
        LIMIT 10
    """
    df_top_products = pd.read_sql_query(top_products_sql, conn)
    top_products_path = os.path.join(GOLD_DIR, "top_products.csv")
    df_top_products.to_csv(top_products_path, index=False)
    print(f"  [OK] Saved Top 10 selling products to: {top_products_path}")

    # ----------------------------------------------------
    # KPI 4: Store Performance
    # ----------------------------------------------------
    print("Running SQL for Store Performance Ranking...")
    store_performance_sql = """
        SELECT 
            s.store_name,
            s.city,
            s.region,
            ROUND(SUM(o.total_amount), 2) AS total_revenue,
            COUNT(o.order_id) AS total_orders
        FROM orders o
        JOIN stores s ON o.store_id = s.store_id
        GROUP BY s.store_id, s.store_name, s.city, s.region
        ORDER BY total_revenue DESC
    """
    df_store_perf = pd.read_sql_query(store_performance_sql, conn)
    store_performance_path = os.path.join(GOLD_DIR, "store_performance.csv")
    df_store_perf.to_csv(store_performance_path, index=False)
    print(f"  [OK] Saved {len(df_store_perf)} stores ranked by sales to: {store_performance_path}")

    # Save SQL queries as permanent views in database for analysis exploration
    cursor = conn.cursor()
    cursor.execute("DROP VIEW IF EXISTS view_low_stock_alerts")
    cursor.execute(f"CREATE VIEW view_low_stock_alerts AS {low_stock_sql}")
    
    cursor.execute("DROP VIEW IF EXISTS view_daily_sales")
    cursor.execute(f"CREATE VIEW view_daily_sales AS {daily_sales_sql}")
    
    cursor.execute("DROP VIEW IF EXISTS view_top_products")
    cursor.execute(f"CREATE VIEW view_top_products AS {top_products_sql}")
    
    cursor.execute("DROP VIEW IF EXISTS view_store_performance")
    cursor.execute(f"CREATE VIEW view_store_performance AS {store_performance_sql}")
    conn.commit()
    print("  [DB] Created SQLite Views (view_low_stock_alerts, view_daily_sales, view_top_products, view_store_performance) for visual dashboard connections.")

def run_gold_computation():
    print("=" * 60)
    print("[START] RUNNING GOLD LAYER COMPUTATION (SQL ENGINE)...")
    print("=" * 60)
    
    # Ensure directories exist
    if not os.path.exists(GOLD_DIR):
        os.makedirs(GOLD_DIR, exist_ok=True)
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
        
    # Open SQLite database connection
    conn = sqlite3.connect(DB_PATH)
    
    try:
        load_silver_to_sqlite(conn)
        compute_kpis(conn)
        print("=" * 60)
        print("[SUCCESS] GOLD LAYER COMPUTATION COMPLETED SUCCESSFULLY!")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"[ERROR] Gold layer computation failed: {str(e)}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    run_gold_computation()
