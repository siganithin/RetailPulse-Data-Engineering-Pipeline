"""
RetailPulse - Data Engineering Pipeline
Visualization Layer: Professional Chart Generator

This script reads Gold KPI outputs and generates three highly polished charts:
1. Horizontal Bar Chart: Top 10 Products by Revenue.
2. Line Chart: Daily Revenue Trend.
3. Vertical Bar Chart: Store Performance by Total Revenue.

The charts are styled to look modern, clean, and professional for a final-year presentation.
They are saved in the 'outputs/' directory.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Enforce non-interactive backend to run cleanly without a GUI
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Setup paths relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_DIR = os.path.join(BASE_DIR, "data", "gold")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

# Curated modern color palette
COLOR_PRIMARY = "#1e3d59"     # Deep Dark Blue
COLOR_SECONDARY = "#17b890"   # Vibrant Teal
COLOR_ACCENT = "#ff6e40"      # Sunset Orange
COLOR_MUTED = "#b3c100"       # Olive Accent
COLOR_GRID = "#e8ecef"        # Light gray for subtle gridlines
COLOR_TEXT = "#2b2b2b"        # Soft black text
COLOR_BG = "#f5f7fa"          # Light canvas background

def set_professional_style(ax, title, xlabel, ylabel):
    """Utility function to apply a consistent, premium design to a Matplotlib axis."""
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15, color=COLOR_PRIMARY)
    ax.set_xlabel(xlabel, fontsize=11, labelpad=8, color=COLOR_TEXT)
    ax.set_ylabel(ylabel, fontsize=11, labelpad=8, color=COLOR_TEXT)
    
    # Grid styling
    ax.grid(True, linestyle="--", alpha=0.5, color=COLOR_GRID)
    ax.set_axisbelow(True)
    
    # Spine removal (clean look)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#cccccc")
        ax.spines[spine].set_linewidth(1.0)
        
    ax.tick_params(colors=COLOR_TEXT, labelsize=10)

def plot_top_products():
    print("Generating Top 10 Products Chart...")
    file_path = os.path.join(GOLD_DIR, "top_products.csv")
    df = pd.read_csv(file_path)
    
    # Sort ascending for horizontal bar chart (so highest is at the top)
    df_sorted = df.sort_values(by="total_revenue", ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 6), facecolor="white")
    
    # Generate horizontal bars with a clean gradient-like color
    bars = ax.barh(
        df_sorted["product_name"], 
        df_sorted["total_revenue"], 
        color=COLOR_PRIMARY, 
        edgecolor=None,
        height=0.6
    )
    
    # Add value labels at the end of each bar
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + (width * 0.01), 
            bar.get_y() + bar.get_height()/2, 
            f"INR {width:,.2f}", 
            va="center", 
            ha="left", 
            fontsize=9, 
            fontweight="bold", 
            color=COLOR_PRIMARY
        )
        
    set_professional_style(
        ax, 
        title="Top 10 Selling Products by Revenue", 
        xlabel="Total Revenue (INR)", 
        ylabel="Product Name"
    )
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUTS_DIR, "top_products.png")
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print(f"  [OK] Saved Top Products chart to: {output_path}")

def plot_daily_sales():
    print("Generating Daily Revenue Trend Chart...")
    file_path = os.path.join(GOLD_DIR, "daily_sales.csv")
    df = pd.read_csv(file_path)
    
    # Convert date to datetime for correct timeline plotting
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")
    
    fig, ax = plt.subplots(figsize=(12, 6), facecolor="white")
    
    # Line plot with markers
    ax.plot(
        df["date"], 
        df["total_revenue"], 
        color=COLOR_ACCENT, 
        linewidth=2.5, 
        marker="o", 
        markersize=6, 
        markerfacecolor=COLOR_PRIMARY, 
        markeredgecolor=COLOR_PRIMARY,
        label="Daily Revenue"
    )
    
    # Add a rolling average line to show trends (7-day window)
    if len(df) >= 7:
        df["rolling_avg"] = df["total_revenue"].rolling(window=7, min_periods=1).mean()
        ax.plot(
            df["date"], 
            df["rolling_avg"], 
            color=COLOR_SECONDARY, 
            linestyle="--", 
            linewidth=2.0, 
            label="7-Day Trend Line"
        )
    
    set_professional_style(
        ax, 
        title="Daily Sales Revenue Trend Over Time", 
        xlabel="Order Date", 
        ylabel="Total Revenue (INR)"
    )
    
    # Formatting date tick labels nicely
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d, %Y"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    fig.autofmt_xdate() # Rotate dates
    
    ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor=COLOR_GRID)
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUTS_DIR, "daily_sales.png")
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print(f"  [OK] Saved Daily Sales chart to: {output_path}")

def plot_store_performance():
    print("Generating Store Performance Chart...")
    file_path = os.path.join(GOLD_DIR, "store_performance.csv")
    df = pd.read_csv(file_path)
    
    # Top 10 stores (we have exactly 10 in stores.csv)
    df_sorted = df.sort_values(by="total_revenue", ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(11, 6), facecolor="white")
    
    # Draw bars
    bars = ax.bar(
        df_sorted["store_name"], 
        df_sorted["total_revenue"], 
        color=COLOR_SECONDARY, 
        edgecolor=None,
        width=0.55
    )
    
    # Add value labels above the bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2, 
            height + (height * 0.01), 
            f"INR {height/1000:.1f}k", 
            va="bottom", 
            ha="center", 
            fontsize=8.5, 
            fontweight="bold", 
            color=COLOR_PRIMARY
        )
        
    set_professional_style(
        ax, 
        title="Store Performance Comparison by Total Sales Revenue", 
        xlabel="Store Name", 
        ylabel="Total Revenue (INR)"
    )
    
    # Rotate labels
    plt.xticks(rotation=25, ha="right")
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUTS_DIR, "store_sales.png")
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print(f"  [OK] Saved Store Sales chart to: {output_path}")

def run_visualization():
    print("=" * 60)
    print("[START] RUNNING STATIC CHART VISUALIZATION GENERATOR...")
    print("=" * 60)
    
    # Ensure outputs folder exists
    if not os.path.exists(OUTPUTS_DIR):
        print(f"Creating outputs folder: {OUTPUTS_DIR}")
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        
    try:
        plot_top_products()
        plot_daily_sales()
        plot_store_performance()
        print("=" * 60)
        print("[SUCCESS] VISUALIZATION IMAGES GENERATED SUCCESSFULLY!")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"[ERROR] Visualization generation failed: {str(e)}")
        raise e

if __name__ == "__main__":
    run_visualization()
