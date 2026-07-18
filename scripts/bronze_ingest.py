"""
RetailPulse - Data Engineering Pipeline
Bronze Layer: Raw Data Ingestion

This script is the first stage of the Medallion Architecture data pipeline.
Its sole responsibility is to copy the raw CSV datasets from the source folder 
into the local bronze directory without making any modifications. This ensures 
that an untouched copy of the original source data is preserved for auditability.

As a best practice, an ingestion audit is performed (counting rows/columns)
to verify that the copy process succeeded without corruption.
"""

import os
import shutil
import pandas as pd

# Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(os.path.dirname(BASE_DIR), "Smart Metadata-Driven Retail Supply Chain Pipeline")
BRONZE_DIR = os.path.join(BASE_DIR, "data", "bronze")

# Mapping of source filenames to target filenames
# Renaming inventory_.csv to inventory.csv for cleaner downstream handling
FILE_MAPPING = {
    "orders.csv": "orders.csv",
    "inventory_.csv": "inventory.csv",
    "products.csv": "products.csv",
    "stores.csv": "stores.csv",
    "suppliers.csv": "suppliers.csv"
}

def run_bronze_ingestion():
    print("=" * 60)
    print("[START] RUNNING BRONZE INGESTION LAYER...")
    print("=" * 60)
    
    # Ensure bronze directory exists
    if not os.path.exists(BRONZE_DIR):
        print(f"Creating bronze folder: {BRONZE_DIR}")
        os.makedirs(BRONZE_DIR, exist_ok=True)
    
    # Audit trail dictionary to keep track of row/column counts
    audit_trail = {}
    
    for src_file, dest_file in FILE_MAPPING.items():
        src_path = os.path.join(SOURCE_DIR, src_file)
        dest_path = os.path.join(BRONZE_DIR, dest_file)
        
        # Checking if raw source files are present
        if not os.path.exists(src_path):
            print(f"[ERROR] Source file not found: {src_path}")
            print("Please make sure the source folder contains the required CSV files.")
            raise FileNotFoundError(f"Missing required raw file: {src_file}")
            
        print(f"Copying: {src_file} -> {dest_file}...")
        
        try:
            # Copy file without modification
            shutil.copy2(src_path, dest_path)
            
            # Load copied CSV briefly to perform audit count
            df = pd.read_csv(dest_path)
            rows, cols = df.shape
            audit_trail[dest_file] = {"rows": rows, "columns": cols}
            print(f"[OK] Ingested successfully. Size: {rows} rows x {cols} columns.")
            
        except Exception as e:
            print(f"[ERROR] Failed to ingest {src_file}: {str(e)}")
            raise e
            
    print("\n[REPORT] --- BRONZE INGESTION AUDIT REPORT ---")
    for filename, stats in audit_trail.items():
        print(f"  {filename:<15} : {stats['rows']:>4} rows, {stats['columns']:>2} columns")
    print("=" * 60)
    print("[SUCCESS] BRONZE INGESTION COMPLETED SUCCESSFULLY!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_bronze_ingestion()
