# Databricks Notebook source
# MAGIC %md
# MAGIC # RetailPulse: Smart Metadata-Driven Retail Supply Chain Pipeline
# MAGIC ### Data Engineering Project (Medallion Architecture)
# MAGIC 
# MAGIC This notebook implements the **RetailPulse Data Pipeline** in the cloud using **PySpark** and **Spark SQL**.
# MAGIC It mirrors the local Python/Pandas pipeline but is built for massive scale on a Databricks cluster.
# MAGIC 
# MAGIC **Medallion Architecture Stages:**
# MAGIC 1. **Bronze Layer**: Ingest raw CSV data from DBFS (Databricks File System) and write as raw Delta tables.
# MAGIC 2. **Silver Layer**: Clean columns, drop duplicates/nulls, enforce schemas, and write as cleaned Delta tables.
# MAGIC 3. **Gold Layer**: Compute core retail KPIs and performance ranks using Spark SQL queries.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Initialize Session and Define Paths
# MAGIC It is assumed that the raw CSV files are uploaded to DBFS at `/FileStore/tables/retail_pulse/`.

# COMMAND ----------

from pyspark.sql.types import *
from pyspark.sql.functions import *

# Define path where raw files are uploaded
DBFS_SOURCE_DIR = "/FileStore/tables/retail_pulse/"

# Initialize database in Databricks Catalog
spark.sql("CREATE DATABASE IF NOT EXISTS retail_pulse_db")
spark.sql("USE retail_pulse_db")
print("Database initialized.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Bronze Ingestion (Raw Delta Tables)
# MAGIC The CSV files are loaded from DBFS and saved as Delta tables directly into the database. No changes are applied.

# COMMAND ----------

datasets = ["orders", "inventory", "products", "stores", "suppliers"]

for dataset in datasets:
    # Handle the fact that inventory raw file was named inventory_.csv in source folder
    filename = "inventory_.csv" if dataset == "inventory" else f"{dataset}.csv"
    path = f"{DBFS_SOURCE_DIR}{filename}"
    
    print(f"Ingesting raw dataset: {dataset} from {path}...")
    
    # Read raw CSV
    raw_df = spark.read.format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(path)
        
    # Write to Bronze layer Delta table
    bronze_table_name = f"bronze_{dataset}"
    raw_df.write.format("delta").mode("overwrite").saveAsTable(bronze_table_name)
    print(f"✅ Ingested {raw_df.count()} rows into Bronze table '{bronze_table_name}'")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Silver Layer (Data Cleaning & Enrichment)
# MAGIC Each table is cleaned and written to a Silver Delta table.

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.1 Clean Products, Stores, Suppliers (Dimension Tables)

# COMMAND ----------

# Products Dimension
df_prod = spark.read.table("bronze_products").dropna(subset=["product_id"]).dropDuplicates(["product_id"])
df_prod = df_prod.select([trim(col(c)).alias(c) if t == "string" else col(c) for c, t in df_prod.dtypes])
df_prod.write.format("delta").mode("overwrite").saveAsTable("silver_products")

# Stores Dimension
df_stores = spark.read.table("bronze_stores").dropna(subset=["store_id"]).dropDuplicates(["store_id"])
df_stores = df_stores.select([trim(col(c)).alias(c) if t == "string" else col(c) for c, t in df_stores.dtypes])
df_stores.write.format("delta").mode("overwrite").saveAsTable("silver_stores")

# Suppliers Dimension
df_supp = spark.read.table("bronze_suppliers").dropna(subset=["supplier_id"]).dropDuplicates(["supplier_id"])
df_supp = df_supp.select([trim(col(c)).alias(c) if t == "string" else col(c) for c, t in df_supp.dtypes])
df_supp.write.format("delta").mode("overwrite").saveAsTable("silver_suppliers")

print("✅ Dimension tables cleaned and written to Silver.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.2 Clean Orders Fact Table

# COMMAND ----------

# Load Bronze orders
df_orders = spark.read.table("bronze_orders")

# Drop null rows in critical columns
df_orders = df_orders.dropna(subset=["order_id", "product_id", "store_id", "quantity", "price", "order_date"])

# Remove duplicate order ids
df_orders = df_orders.dropDuplicates(["order_id"])

# Enforce clean datatypes and date formatting
df_orders = df_orders \
    .withColumn("order_id", trim(col("order_id"))) \
    .withColumn("product_id", trim(col("product_id"))) \
    .withColumn("store_id", trim(col("store_id"))) \
    .withColumn("quantity", col("quantity").cast(IntegerType())) \
    .withColumn("price", col("price").cast(DoubleType())) \
    .withColumn("order_date", to_date(col("order_date"), "yyyy-MM-dd"))

# Filter positive price and quantity
df_orders = df_orders.filter((col("quantity") > 0) & (col("price") > 0))

# Enrichment: total_amount column
df_orders = df_orders.withColumn("total_amount", round(col("quantity") * col("price"), 2))

# Save to Silver Table
df_orders.write.format("delta").mode("overwrite").saveAsTable("silver_orders")
print(f"✅ Orders cleaned. Total rows: {df_orders.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.3 Clean Inventory Table

# COMMAND ----------

# Load Bronze inventory
df_inv = spark.read.table("bronze_inventory")

# Clean null values and duplicates
df_inv = df_inv.dropna(subset=["product_id", "store_id", "stock_level", "reorder_level", "last_updated"])
df_inv = df_inv.dropDuplicates(["product_id", "store_id"])

# Enforce data types and constraints
df_inv = df_inv \
    .withColumn("product_id", trim(col("product_id"))) \
    .withColumn("store_id", trim(col("store_id"))) \
    .withColumn("stock_level", col("stock_level").cast(IntegerType())) \
    .withColumn("reorder_level", col("reorder_level").cast(IntegerType())) \
    .withColumn("last_updated", to_date(col("last_updated"), "yyyy-MM-dd"))

df_inv = df_inv.filter((col("stock_level") >= 0) & (col("reorder_level") >= 0))

# Enrichment: add low_stock_flag (stock_level < reorder_level)
df_inv = df_inv.withColumn("low_stock_flag", when(col("stock_level") < col("reorder_level"), 1).otherwise(0))

# Save to Silver Table
df_inv.write.format("delta").mode("overwrite").saveAsTable("silver_inventory")
print(f"✅ Inventory cleaned. Total rows: {df_inv.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Gold Layer (Compute KPIs using Spark SQL)
# MAGIC Now Spark SQL queries are run to create final Gold KPI tables for the visualization dashboard.

# COMMAND ----------

# Register Silver Delta tables as Spark SQL views for SQL access
spark.read.table("silver_orders").createOrReplaceTempView("orders")
spark.read.table("silver_inventory").createOrReplaceTempView("inventory")
spark.read.table("silver_products").createOrReplaceTempView("products")
spark.read.table("silver_stores").createOrReplaceTempView("stores")
spark.read.table("silver_suppliers").createOrReplaceTempView("suppliers")

# COMMAND ----------

# MAGIC %md
# MAGIC ### KPI 1: Low Stock Alerts
# MAGIC Find product-store combinations where current stock level has fallen below the reorder threshold.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold_low_stock_alerts AS
# MAGIC SELECT 
# MAGIC     p.product_name,
# MAGIC     s.store_name,
# MAGIC     i.stock_level,
# MAGIC     i.reorder_level,
# MAGIC     (i.reorder_level - i.stock_level) AS units_needed,
# MAGIC     p.category,
# MAGIC     s.city,
# MAGIC     sup.supplier_name,
# MAGIC     sup.lead_time_days
# MAGIC FROM inventory i
# MAGIC JOIN products p ON i.product_id = p.product_id
# MAGIC JOIN stores s ON i.store_id = s.store_id
# MAGIC JOIN suppliers sup ON p.supplier_id = sup.supplier_id
# MAGIC WHERE i.stock_level < i.reorder_level
# MAGIC ORDER BY units_needed DESC;
# MAGIC 
# MAGIC SELECT * FROM gold_low_stock_alerts LIMIT 5;

# COMMAND ----------

# MAGIC %md
# MAGIC ### KPI 2: Daily Sales Summary
# MAGIC Aggregate revenue and average order value day-by-day.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold_daily_sales AS
# MAGIC SELECT 
# MAGIC     order_date AS date,
# MAGIC     COUNT(order_id) AS total_orders,
# MAGIC     ROUND(SUM(total_amount), 2) AS total_revenue,
# MAGIC     ROUND(AVG(total_amount), 2) AS avg_order_val
# MAGIC FROM orders
# MAGIC GROUP BY order_date
# MAGIC ORDER BY order_date ASC;
# MAGIC 
# MAGIC SELECT * FROM gold_daily_sales LIMIT 5;

# COMMAND ----------

# MAGIC %md
# MAGIC ### KPI 3: Top 10 Best Selling Products
# MAGIC Rank top selling products based on total sales revenue.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold_top_products AS
# MAGIC SELECT 
# MAGIC     p.product_name,
# MAGIC     p.category,
# MAGIC     ROUND(SUM(o.total_amount), 2) AS total_revenue,
# MAGIC     SUM(o.quantity) AS units_sold
# MAGIC FROM orders o
# MAGIC JOIN products p ON o.product_id = p.product_id
# MAGIC GROUP BY p.product_id, p.product_name, p.category
# MAGIC ORDER BY total_revenue DESC
# MAGIC LIMIT 10;
# MAGIC 
# MAGIC SELECT * FROM gold_top_products;

# COMMAND ----------

# MAGIC %md
# MAGIC ### KPI 4: Store Performance Ranking
# MAGIC Rank retail stores based on total sales revenue generated.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold_store_performance AS
# MAGIC SELECT 
# MAGIC     s.store_name,
# MAGIC     s.city,
# MAGIC     s.region,
# MAGIC     ROUND(SUM(o.total_amount), 2) AS total_revenue,
# MAGIC     COUNT(o.order_id) AS total_orders
# MAGIC FROM orders o
# MAGIC JOIN stores s ON o.store_id = s.store_id
# MAGIC GROUP BY s.store_id, s.store_name, s.city, s.region
# MAGIC ORDER BY total_revenue DESC;
# MAGIC 
# MAGIC SELECT * FROM gold_store_performance;
