"""
RetailPulse - End-to-End Retail Supply Chain Pipeline
Main Pipeline Orchestrator

This script is the main entry point to run the data engineering pipeline.
It triggers each stage of the Medallion Architecture sequentially:
1. Bronze Layer (Ingestion): Copies raw CSV files and creates ingestion logs.
2. Silver Layer (Processing): Cleans, validates, and enriches dataset schemas.
3. Gold Layer (Analytics): Imports Silver datasets into SQLite and queries KPIs.
4. Visualizations (Matplotlib): Generates premium chart images in the 'outputs/' folder.

To run:
    python main.py
"""

import time
import sys
import os

# Append current directory to path so script imports work cleanly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from scripts.bronze_ingest import run_bronze_ingestion
from scripts.silver_process import run_silver_processing
from scripts.gold_compute import run_gold_computation
from scripts.visualize import run_visualization

def print_banner():
    banner = """
======================================================================
  ____       _             _ _ ____        _             
 |  _ \\  ___| |_ __ _     | | |  _ \\ _   _| |___  ___   
 | |_) |/ _ \\ __/ _` | ___| | | |_) | | | | / __|/ _ \\  
 |  _ <|  __/ || (_| |/ __| | |  __/| |_| | \\__ \\  __/  
 |_| \_\\\\___|\\__\\__,_|\\___|_|_|_|    \\__,_|_|___/\\___|  
                                                        
   Retail Supply Chain Data Engineering Medallion Pipeline
   Academic Year 2024-25 | CSE Internship Major Project
======================================================================
"""
    print(banner)

def main():
    print_banner()
    start_time = time.time()
    
    try:
        # Stage 1: Bronze Ingestion
        run_bronze_ingestion()
        
        # Stage 2: Silver Cleaning & Processing
        run_silver_processing()
        
        # Stage 3: Gold SQL Analytics
        run_gold_computation()
        
        # Stage 4: Visualizations
        run_visualization()
        
        elapsed_time = time.time() - start_time
        print("=" * 70)
        print("[SUCCESS] PIPELINE RUN COMPLETED SUCCESSFULLY!")
        print(f"Elapsed Time: {elapsed_time:.2f} seconds")
        print("Processed silver datasets saved to: /data/silver/")
        print("Gold Analytics CSVs saved to: /data/gold/")
        print("SQLite Database: /database/retail_pulse.db")
        print("Visual charts saved to: /outputs/")
        print("=" * 70)
        print("\nNext Step: Launch the interactive Web Dashboard using:")
        print("   streamlit run dashboard.py\n")
        
    except Exception as e:
        print("\n[ERROR] PIPELINE RUN FAILED!")
        print(f"Error Details: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
