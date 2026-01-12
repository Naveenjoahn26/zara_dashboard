from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from contextlib import asynccontextmanager

from data_loader import load_and_clean_sales_data
from analytics import (
    get_overview_metrics,
    get_sales_by_product,
    get_sales_by_category,
    get_sales_trend,
    get_raw_sales_data
)

# -----------------------------
# Lifespan Event (Startup / Shutdown)
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.sales_df = load_and_clean_sales_data()

    if app.state.sales_df.empty:
        raise RuntimeError("Sales data is empty after cleaning")

    yield

    # Shutdown (optional cleanup)
    # e.g. close DB connections


# -----------------------------
# App Initialization
# -----------------------------
app = FastAPI(
    title="Sales Dashboard API",
    description="Backend API for Sales Analytics Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# -----------------------------
# Enable CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "sales-analytics-api",
        "version": "1.0.0"
    }

# -----------------------------
# Overview Metrics
# -----------------------------
@app.get("/analytics/overview")
def analytics_overview(
    start_date: Optional[str] = Query(None, examples="2023-01-01"),
    end_date: Optional[str] = Query(None, examples="2023-12-31")
):
    return get_overview_metrics(
        app.state.sales_df,
        start_date=start_date,
        end_date=end_date
    )

# -----------------------------
# Sales by Product
# -----------------------------
@app.get("/analytics/sales-by-product")
def analytics_sales_by_product(
    limit: int = Query(10, ge=1, le=50),
    sort_by: str = Query("revenue", pattern="^(revenue|quantity_sold)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    return get_sales_by_product(
        app.state.sales_df,
        limit=limit,
        sort_by=sort_by,
        start_date=start_date,
        end_date=end_date
    )

# -----------------------------
# Sales by Category
# -----------------------------
@app.get("/analytics/sales-by-category")
def analytics_sales_by_category(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    return get_sales_by_category(
        app.state.sales_df,
        start_date=start_date,
        end_date=end_date
    )

# -----------------------------
# Sales Trend
# -----------------------------
@app.get("/analytics/sales-trend")
def analytics_sales_trend(
    interval: str = Query("monthly", pattern="^(daily|monthly)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    return get_sales_trend(
        app.state.sales_df,
        interval=interval,
        start_date=start_date,
        end_date=end_date
    )

# -----------------------------
# Raw Sales Data
# -----------------------------
@app.get("/analytics/raw-sales")
def analytics_raw_sales(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    data = get_raw_sales_data(app.state.sales_df, limit, offset)

    if not data:
        raise HTTPException(status_code=404, detail="No data found")

    return data
