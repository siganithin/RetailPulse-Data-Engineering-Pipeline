"""
RetailPulse - Data Engineering Pipeline
Silver Layer: Data Cleaning & Enrichment

This script is the second stage of the data pipeline.
It reads raw files from 'data/bronze', cleans them, enforces schemas/constraints, 
and enriches the datasets with new useful columns (like order revenue and stock alerts).
Cleaned files are then saved to 'data/silver' as '*_clean.csv'.
"""

import os
import pandas as pd
import numpy as np

# Setup paths relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRONZE_DIR = os.path.join(BASE_DIR, "data", "bronze")
SILVER_DIR = os.path.join(BASE_DIR, "data", "silver")

def clean_orders():
    print("Cleaning Orders dataset...")
    file_path = os.path.join(BRONZE_DIR, "orders.csv")
    df = pd.read_csv(file_path)
    initial_rows = len(df)
    
    # 1. Handle missing values in critical columns
    df = df.dropna(subset=['order_id', 'product_id', 'store_id', 'quantity', 'price', 'order_date'])
    null_dropped = initial_rows - len(df)
    if null_dropped > 0:
        print(f"  [WARNING] Dropped {null_dropped} rows with missing critical information.")
        
    # 2. Deduplicate records based on order_id
    pre_dedup = len(df)
    df = df.drop_duplicates(subset=['order_id'])
    duplicates_dropped = pre_dedup - len(df)
    if duplicates_dropped > 0:
        print(f"  [WARNING] Removed {duplicates_dropped} duplicate order entries.")
        
    # 3. Enforce data types and formats
    df['order_id'] = df['order_id'].astype(str).str.strip()
    df['product_id'] = df['product_id'].astype(str).str.strip()
    df['store_id'] = df['store_id'].astype(str).str.strip()
    df['quantity'] = df['quantity'].astype(int)
    df['price'] = df['price'].astype(float)
    
    # Enforce date format YYYY-MM-DD
    df['order_date'] = pd.to_datetime(df['order_date']).dt.strftime('%Y-%m-%d')
    
    # 4. Enforce business rules / constraints
    # (Orders must have positive quantities and prices)
    valid_mask = (df['quantity'] > 0) & (df['price'] > 0)
    invalid_count = len(df) - valid_mask.sum()
    if invalid_count > 0:
        print(f"  [WARNING] Filtering out {invalid_count} records due to invalid price/quantity constraints.")
        df = df[valid_mask]
        
    # 5. Enrichment: Add total amount
    df['total_amount'] = np.round(df['quantity'] * df['price'], 2)
    
    # Save cleaned file
    output_path = os.path.join(SILVER_DIR, "orders_clean.csv")
    df.to_csv(output_path, index=False)
    print(f"  [OK] Orders cleaned. Rows: {initial_rows} -> {len(df)}. Saved to {output_path}")
    return initial_rows, len(df)

def clean_inventory():
    print("Cleaning Inventory dataset...")
    file_path = os.path.join(BRONZE_DIR, "inventory.csv")
    df = pd.read_csv(file_path)
    initial_rows = len(df)
    
    # 1. Drop nulls
    df = df.dropna(subset=['product_id', 'store_id', 'stock_level', 'reorder_level', 'last_updated'])
    null_dropped = initial_rows - len(df)
    if null_dropped > 0:
        print(f"  [WARNING] Dropped {null_dropped} rows with missing inventory columns.")
        
    # 2. Deduplicate (combination of product_id + store_id should be unique)
    pre_dedup = len(df)
    df = df.drop_duplicates(subset=['product_id', 'store_id'])
    duplicates_dropped = pre_dedup - len(df)
    if duplicates_dropped > 0:
        print(f"  [WARNING] Removed {duplicates_dropped} duplicate inventory key matches.")
        
    # 3. Enforce data types
    df['product_id'] = df['product_id'].astype(str).str.strip()
    df['store_id'] = df['store_id'].astype(str).str.strip()
    df['stock_level'] = df['stock_level'].astype(int)
    df['reorder_level'] = df['reorder_level'].astype(int)
    df['last_updated'] = pd.to_datetime(df['last_updated']).dt.strftime('%Y-%m-%d')
    
    # 4. Enforce constraints
    valid_mask = (df['stock_level'] >= 0) & (df['reorder_level'] >= 0)
    invalid_count = len(df) - valid_mask.sum()
    if invalid_count > 0:
        print(f"  [WARNING] Filtering out {invalid_count} records due to negative stock level values.")
        df = df[valid_mask]
        
    # 5. Enrichment: Add low_stock_flag (stock_level < reorder_level)
    df['low_stock_flag'] = (df['stock_level'] < df['reorder_level']).astype(int)
    
    output_path = os.path.join(SILVER_DIR, "inventory_clean.csv")
    df.to_csv(output_path, index=False)
    print(f"  [OK] Inventory cleaned. Rows: {initial_rows} -> {len(df)}. Saved to {output_path}")
    return initial_rows, len(df)

def clean_dimension_table(filename, pkey):
    print(f"Cleaning {filename} (Dimension)...")
    file_path = os.path.join(BRONZE_DIR, filename)
    df = pd.read_csv(file_path)
    initial_rows = len(df)
    
    # Drop completely empty row matches or rows missing the primary key
    df = df.dropna(subset=[pkey])
    
    # Deduplicate on primary key
    df = df.drop_duplicates(subset=[pkey])
    
    # Clean text columns: strip whitespaces
    for col in df.select_dtypes(include=[object]).columns:
        df[col] = df[col].astype(str).str.strip()
        
    # Save cleaned file
    clean_filename = filename.replace('.csv', '_clean.csv')
    output_path = os.path.join(SILVER_DIR, clean_filename)
    df.to_csv(output_path, index=False)
    
    print(f"  [OK] {filename} cleaned. Rows: {initial_rows} -> {len(df)}. Saved to {output_path}")
    return initial_rows, len(df)

def run_silver_processing():
    print("=" * 60)
    print("[START] RUNNING SILVER DATA CLEANING LAYER...")
    print("=" * 60)
    
    # Ensure silver directory exists
    if not os.path.exists(SILVER_DIR):
        print(f"Creating silver folder: {SILVER_DIR}")
        os.makedirs(SILVER_DIR, exist_ok=True)
        
    # Keep run logs
    stats = {}
    
    # Clean dimensions
    stats['products.csv'] = clean_dimension_table("products.csv", "product_id")
    stats['stores.csv'] = clean_dimension_table("stores.csv", "store_id")
    stats['suppliers.csv'] = clean_dimension_table("suppliers.csv", "supplier_id")
    
    # Clean facts
    stats['orders.csv'] = clean_orders()
    stats['inventory.csv'] = clean_inventory()
    
    print("\n[REPORT] --- SILVER LAYER AUDIT SUMMARY ---")
    print(f"{'Dataset':<20} | {'Raw Rows':<10} | {'Cleaned Rows':<12}")
    print("-" * 50)
    for name, (raw, clean) in stats.items():
        print(f"{name:<20} | {raw:<10} | {clean:<12}")
    print("=" * 60)
    print("[SUCCESS] SILVER DATA CLEANING COMPLETED SUCCESSFULLY!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_silver_processing()
