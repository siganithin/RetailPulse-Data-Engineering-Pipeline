# RetailPulse
## Smart Metadata-Driven Retail Supply Chain Pipeline

## Project Background

RetailPulse was developed as the final major project for the **Celebal Excellence Internship (CEI)**. The project demonstrates the design and implementation of an end-to-end retail supply chain data engineering pipeline using the Medallion Architecture (Bronze, Silver, Gold), with a scalable implementation in Databricks using PySpark.


An end-to-end data engineering project that implements the **Medallion Architecture** (Bronze → Silver → Gold) to process retail supply chain data and generate actionable business insights.

RetailPulse is an end-to-end retail data engineering application implementing the Medallion Architecture (Bronze → Silver → Gold). The application integrates ETL pipelines, SQL analytics, inventory monitoring, demand simulation, and enterprise scalability concepts using Databricks (PySpark).

---

## Overview

RetailPulse addresses core supply chain challenges faced by retail organisations:

- **Fragmented data sources** — orders, inventory, products, stores, and suppliers stored as separate raw files
- **Lack of demand visibility** — no consolidated view of daily sales trends or product performance
- **Stock management gaps** — stockouts and overstock situations go undetected without automated alerts
- **No replenishment intelligence** — manual processes miss supplier lead times and demand spikes

The pipeline automates ingestion, cleaning, enrichment, and analytics across all five datasets, producing real-time KPIs through an interactive dashboard.

---

## Features

- Bronze → Silver → Gold medallion pipeline
- Automated data cleaning and validation
- Metadata-driven processing
- SQLite analytics engine with SQL Views
- Interactive Streamlit dashboard
- Demand spike simulation (7-day forecast)
- Live SQL Explorer with schema reference
- Static KPI chart generation (Matplotlib)
- Low stock alerts with supplier lead time context
- Databricks scalability implementation (PySpark + Delta Lake)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| Data Processing | Pandas, NumPy |
| Database | SQLite3 |
| Query Language | SQL |
| Dashboard | Streamlit |
| Charts | Plotly, Matplotlib |
| Cloud Scale | PySpark, Databricks, Delta Lake |
| Version Control | Git, GitHub |

---

## Project Architecture

```
Raw CSV Files
     ↓
  Bronze Layer         ← Ingestion (no modification)
     ↓
  Silver Layer         ← Cleaning, validation, enrichment
     ↓
  Gold Layer           ← KPI computation via SQL
     ↓
  SQLite Database      ← retail_pulse.db
     ↓
  Streamlit Dashboard  ← Interactive analytics UI
```

**Enterprise Extension (Databricks)**

```
Raw CSV → DBFS
     ↓
  Bronze Delta Table
     ↓
  Silver Delta Table
     ↓
  Gold Delta Table
     ↓
  Spark SQL
     ↓
  Power BI / Tableau / Streamlit
```

---

## Project Modules

### Bronze Layer — `scripts/bronze_ingest.py`
Copies raw datasets from the source directory to `data/bronze/` without any modification. Preserves an immutable audit trail of original source files. Generates a row/column count audit report on completion.

### Silver Layer — `scripts/silver_process.py`
Cleans, validates, standardises, and enriches all five datasets:
- Removes null values in critical columns
- Deduplicates records by primary key
- Enforces data types and ISO date formatting
- Adds derived columns: `total_amount` and `low_stock_flag`

### Gold Layer — `scripts/gold_compute.py`
Loads cleaned Silver CSVs into a local SQLite database and computes four core KPIs using SQL:
- Low Stock Alerts
- Daily Sales Summary
- Top 10 Products by Revenue
- Store Performance Rankings

### Dashboard — `dashboard.py`
Interactive Streamlit web application featuring:
- Live KPI metric cards
- Filter controls by region and product category
- Daily revenue trend charts
- Store leaderboard
- Stockout alert table with colour-coded severity
- Demand spike simulator
- SQL Explorer terminal
- Enterprise scalability documentation
- Engineering decisions and project journey

### Visualization — `scripts/visualize.py`
Generates three presentation-ready static chart images saved to `outputs/`:
- Top products horizontal bar chart
- Daily sales line chart with rolling average
- Store performance comparison bar chart

### Databricks Notebook — `notebooks/retail_pulse_databricks.py`
Complete PySpark implementation of the Medallion Architecture for Databricks Community Edition. Replaces Pandas with Spark DataFrames, CSVs with Delta Lake tables, and SQLite with Spark SQL.

---

## KPIs Generated

| KPI | Description |
|---|---|
| Low Stock Alerts | Products below reorder threshold with supplier lead times |
| Daily Sales | Revenue and order count aggregated by day |
| Top Products | Top 10 SKUs ranked by total revenue |
| Store Performance | Branch-level revenue and order volume ranking |
| Demand Simulation | 7-day stockout forecast under configurable demand spikes |
| Category Breakdown | Revenue and units by product category |

---

## Folder Structure

```
Smart Metadata-Driven Retail Supply Chain Pipeline_major_proj/
│
├── data/
│   ├── bronze/          ← Raw CSVs (untouched copies)
│   ├── silver/          ← Cleaned and enriched CSVs
│   └── gold/            ← Aggregated KPI output CSVs
│
├── database/
│   └── retail_pulse.db  ← SQLite database with tables and Views
│
├── notebooks/
│   └── retail_pulse_databricks.py  ← PySpark implementation
│
├── scripts/
│   ├── bronze_ingest.py
│   ├── silver_process.py
│   ├── gold_compute.py
│   └── visualize.py
│
├── outputs/
│   ├── top_products.png
│   ├── daily_sales.png
│   └── store_sales.png
│
├── dashboard.py         ← Streamlit web application
├── main.py              ← Pipeline orchestrator
├── requirements.txt     ← Python dependencies
└── README.md
```

---

## How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Data Pipeline

```bash
python main.py
```

This triggers all four stages in sequence: Bronze ingestion → Silver cleaning → Gold SQL analytics → Static chart generation.

### 3. Launch the Dashboard

```bash
streamlit run dashboard.py
```

Open `http://localhost:8501` in your browser.

---

## Databricks Setup

To run the enterprise version on Databricks Community Edition:

1. Create a free account at [community.cloud.databricks.com](https://community.cloud.databricks.com)
2. Create a cluster — Single Node, Runtime 13.3 LTS
3. Upload the 5 raw CSV files to DBFS at `/FileStore/tables/retail_pulse/`
4. Import `notebooks/retail_pulse_databricks.py` into your Workspace
5. Attach the notebook to your cluster and click **Run All**

The notebook will automatically create Bronze, Silver, and Gold Delta tables in the `retail_pulse_db` catalog.

---

## Local vs Enterprise Comparison

| Aspect | Local | Databricks |
|---|---|---|
| Language | Python | PySpark |
| DataFrames | Pandas | Spark DataFrames |
| Storage | CSV Files | Delta Lake |
| Query Engine | SQLite | Spark SQL |
| Execution | Single Machine | Distributed Cluster |
| Dashboard | Streamlit | Power BI / Tableau |
| Scale | Hundreds of rows | Millions of rows |

---

## Future Scope

- Azure Data Factory for pipeline orchestration
- Azure Blob Storage for cloud data storage
- Apache Kafka for real-time streaming ingestion
- Delta Live Tables for automated pipeline management
- Power BI dashboards for enterprise reporting
- Machine Learning based demand forecasting
- Apache Airflow for automated scheduling

---

## Author

**Nithin Siga**  
B.Tech Computer Science Engineering  
CVR College of Engineering  

Data Engineering · Python · SQL · PySpark · Databricks
