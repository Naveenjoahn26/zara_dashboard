import os
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager
import pandas as pd
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from data_loader import load_and_clean_sales_data, BASE_DIR
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
    # Startup: Load default sales data (start with zara.csv or sample)
    app.state.active_dataset = "zara.csv" if (BASE_DIR / "zara.csv").exists() else "sample_sales_data.csv"
    app.state.sales_df = load_and_clean_sales_data(BASE_DIR / app.state.active_dataset)

    if app.state.sales_df.empty:
        raise RuntimeError("Sales data is empty after cleaning")

    yield

    # Shutdown (optional cleanup)


# -----------------------------
# App Initialization
# -----------------------------
app = FastAPI(
    title="Sales Analytics Dashboard API",
    description="High-Performance Reverse Engineered Backend API for Sales Analytics",
    version="1.1.0",
    lifespan=lifespan
)

# -----------------------------
# Enable CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_df() -> pd.DataFrame:
    """Helper to safely access or lazily load sales DataFrame."""
    if not hasattr(app.state, "sales_df") or app.state.sales_df is None:
        active = getattr(app.state, "active_dataset", "zara.csv" if (BASE_DIR / "zara.csv").exists() else "sample_sales_data.csv")
        target_path = BASE_DIR / active if (BASE_DIR / active).exists() else BASE_DIR / "zara.csv"
        app.state.active_dataset = target_path.name
        app.state.sales_df = load_and_clean_sales_data(target_path)
    return app.state.sales_df


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health_check():
    df = get_current_df()
    return {
        "status": "ok",
        "service": "sales-analytics-api",
        "version": "1.1.0",
        "active_dataset": getattr(app.state, "active_dataset", "zara.csv"),
        "total_records": len(df)
    }


# -----------------------------
# Dataset Management Endpoints
# -----------------------------
@app.get("/analytics/datasets")
def list_datasets():
    csv_files = [f.name for f in BASE_DIR.glob("*.csv")]
    return {
        "available_datasets": sorted(csv_files),
        "active_dataset": getattr(app.state, "active_dataset", "zara.csv")
    }


class SwitchDatasetRequest(BaseModel):
    dataset_name: str


@app.post("/analytics/switch-dataset")
def switch_dataset(req: SwitchDatasetRequest):
    target = BASE_DIR / req.dataset_name
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Dataset {req.dataset_name} not found")

    try:
        new_df = load_and_clean_sales_data(target)
        app.state.sales_df = new_df
        app.state.active_dataset = req.dataset_name
        return {
            "status": "success",
            "active_dataset": req.dataset_name,
            "total_records": len(new_df)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load dataset: {str(e)}")


# -----------------------------
# Metadata / Filters
# -----------------------------
@app.get("/analytics/filters")
def analytics_filters():
    df = get_current_df()
    min_date = df["date"].min()
    max_date = df["date"].max()
    categories = sorted(df["category"].dropna().unique().tolist())

    return {
        "categories": categories,
        "date_range": {
            "min_date": min_date.strftime("%Y-%m-%d") if pd.notna(min_date) else None,
            "max_date": max_date.strftime("%Y-%m-%d") if pd.notna(max_date) else None
        },
        "total_records": len(df),
        "active_dataset": getattr(app.state, "active_dataset", "zara.csv")
    }


# -----------------------------
# Overview Metrics
# -----------------------------
@app.get("/analytics/overview")
def analytics_overview(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD")
):
    df = get_current_df()
    return get_overview_metrics(
        df,
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
    df = get_current_df()
    return get_sales_by_product(
        df,
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
    df = get_current_df()
    return get_sales_by_category(
        df,
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
    df = get_current_df()
    return get_sales_trend(
        df,
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
    df = get_current_df()
    data = get_raw_sales_data(df, limit, offset)

    if not data:
        raise HTTPException(status_code=404, detail="No data found")

    return data


# -----------------------------
# Serve Built React Frontend SPA (Single-Port Full-Stack)
# -----------------------------
DIST_DIR = BASE_DIR / "frontend" / "dist"
if (DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")


@app.get("/")
def serve_index():
    index_html = DIST_DIR / "index.html"
    if index_html.exists():
        return FileResponse(index_html)
    return {"message": "Sales Analytics Dashboard API running. Frontend not yet built in frontend/dist."}


@app.get("/{full_path:path}")
def serve_spa_fallback(full_path: str):
    if full_path.startswith(("analytics", "health", "docs", "openapi.json", "redoc", "assets")):
        raise HTTPException(status_code=404, detail="Endpoint not found")
    index_html = DIST_DIR / "index.html"
    if index_html.exists():
        return FileResponse(index_html)
    raise HTTPException(status_code=404, detail="Frontend index.html not found")
