# RetailPulse
## Smart Metadata-Driven Retail Supply Chain Pipeline

**Live Demo:** https://retailpulse-data-engineering-pipeline-d5npe9nithin649.streamlit.app/

---

## Project Background

RetailPulse was developed as the Final Major Project for the Celebal Excellence Internship (CEI). It is an end-to-end retail data engineering application that transforms raw retail supply chain data into analytics-ready datasets using the Medallion Architecture (Bronze → Silver → Gold). The project integrates automated ETL pipelines, SQL analytics, inventory monitoring, demand simulation, and interactive dashboards to support data-driven decision-making. It also demonstrates enterprise-scale data processing using Databricks and PySpark, showcasing how the solution can scale from a local implementation to a distributed big data environment.

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

## Repository Highlights

- End-to-end Medallion Architecture implementation
- Separate Bronze, Silver, and Gold processing layers
- Local analytics using SQLite
- Enterprise implementation using Databricks & PySpark
- Interactive Streamlit Dashboard
- Spark SQL analytics
- Delta Lake implementation
- Metadata-driven ETL pipeline

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
      │
      ▼
Bronze Layer (Raw Delta Tables)
      │
      ▼
Silver Layer (Cleaning & Validation)
      │
      ▼
Gold Layer (Business KPIs)
      │
      ▼
Spark SQL / SQLite Analytics
      │
      ▼
Interactive Streamlit Dashboard
```

**Enterprise Extension (Databricks)**

```
Raw CSV Files
      │
      ▼
Databricks Workspace
      │
      ▼
Bronze Delta Tables
      │
      ▼
Silver Delta Tables
      │
      ▼
Gold Delta Tables
      │
      ▼
Spark SQL
      │
      ▼
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

### Databricks Notebook — `notebooks/RetailPulse_Enterprise_Pipeline_Final.ipynb`
Complete PySpark implementation of the Medallion Architecture using Databricks Community Edition. The notebook demonstrates enterprise-scale data engineering using Bronze, Silver, and Gold Delta Tables, Spark SQL analytics, and Delta Lake storage.

**Notebook Highlights**
- Bronze Layer — Raw CSV ingestion into Delta Tables
- Silver Layer — Data cleaning, validation, and transformation
- Gold Layer — Business KPI generation
- Spark SQL analytics
- Delta Lake implementation

---

## Business KPIs

| KPI | Description |
|---|---|
| Daily Sales Summary | Revenue and quantity sold by day |
| Top Products | Highest revenue-generating products |
| Store Performance | Revenue generated by each store |
| Low Stock Alerts | Products below reorder threshold |
| Demand Spike Simulation | Dashboard-based demand forecasting |
| Category Revenue Breakdown | Revenue by product category |

---

## Project Workflow

1. Ingest raw retail datasets
2. Store immutable Bronze copies
3. Clean and enrich data in Silver
4. Compute business KPIs in Gold
5. Store analytics-ready data
6. Visualize KPIs through Streamlit Dashboard
7. Scale the pipeline using Databricks and Delta Lake

---

## Folder Structure

```
RetailPulse-Data-Engineering-Pipeline/
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
│   └── RetailPulse_Enterprise_Pipeline_Final.ipynb  ← PySpark implementation
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

The enterprise notebook (`notebooks/RetailPulse_Enterprise_Pipeline_Final.ipynb`) runs on Databricks Community Edition without any additional cluster configuration.

1. Create a free account at [community.cloud.databricks.com](https://community.cloud.databricks.com)
2. Import the notebook: go to **Workspace → Import** and upload `notebooks/RetailPulse_Enterprise_Pipeline_Final.ipynb`
3. Open the notebook and attach it to the available compute
4. Upload the datasets to a Unity Catalog Volume (or your configured workspace path)
5. Update the `SOURCE_PATH` variable in the notebook if required
6. Run all notebook cells to create the Bronze, Silver, and Gold Delta Tables automatically

The notebook will create `retail_pulse_db` with Bronze, Silver, and Gold Delta tables using Spark SQL.

---

## Local vs Enterprise Comparison

| Aspect | Local | Databricks |
|---|---|---|
| Language | Python | PySpark |
| DataFrames | Pandas | Spark DataFrames |
| Storage | CSV Files | Delta Lake |
| Query Engine | SQLite | Spark SQL |
| Execution | Single Machine | Distributed Cluster |
| Dashboard | Streamlit | Streamlit / Power BI / Tableau |
| Scale | Hundreds of rows | Millions of rows |

---

## Skills Demonstrated

- Data Engineering
- ETL Pipeline Development
- PySpark
- Databricks
- Delta Lake
- SQL Analytics
- Data Cleaning & Transformation
- Metadata-driven Processing
- Streamlit Dashboard Development
- Git & GitHub

---

## Future Scope

- Azure Blob Storage for cloud data storage
- Azure Data Factory for pipeline orchestration
- Apache Airflow for automated scheduling
- Apache Kafka for real-time streaming ingestion
- Delta Live Tables for automated pipeline management
- Power BI dashboards for enterprise reporting
- Machine Learning based demand forecasting

---

## Conclusion

RetailPulse demonstrates a complete data engineering workflow — from raw data ingestion to business-ready analytics. The project implements industry-standard practices including the Medallion Architecture, SQL-based KPI computation, and enterprise scalability through Databricks and PySpark. It serves as a practical demonstration of how fragmented retail data can be transformed into actionable supply chain intelligence.

---

## Author

**Nithin Siga**
B.Tech Computer Science Engineering
CVR College of Engineering

Data Engineering · Python · SQL · PySpark · Databricks
