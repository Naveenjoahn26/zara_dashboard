import pytest
import pandas as pd
from datetime import datetime, timedelta

from analytics import (
    filter_by_date,
    get_overview_metrics,
    get_sales_by_product,
    get_sales_by_category,
    get_sales_trend,
    get_raw_sales_data
)


@pytest.fixture
def mock_sales_df():
    data = [
        {"date": pd.Timestamp("2024-01-01 10:00:00"), "product_name": "Puffer Jacket", "category": "Outerwear", "quantity": 10, "price": 100.0, "revenue": 1000.0},
        {"date": pd.Timestamp("2024-01-15 14:30:00"), "product_name": "Wool Sweater", "category": "Knitwear", "quantity": 5, "price": 80.0, "revenue": 400.0},
        {"date": pd.Timestamp("2024-02-01 09:15:00"), "product_name": "Puffer Jacket", "category": "Outerwear", "quantity": 2, "price": 100.0, "revenue": 200.0},
        {"date": pd.Timestamp("2024-02-20 18:00:00"), "product_name": "Leather Boots", "category": "Footwear", "quantity": 4, "price": 150.0, "revenue": 600.0},
        {"date": pd.Timestamp("2024-03-10 11:45:00"), "product_name": "Oxford Shirt", "category": "Shirts", "quantity": 20, "price": 50.0, "revenue": 1000.0},
    ]
    return pd.DataFrame(data)


def test_filter_by_date_range(mock_sales_df):
    # Test Start date only
    f1 = filter_by_date(mock_sales_df, start_date="2024-02-01")
    assert len(f1) == 3

    # Test End date only (inclusive of whole day)
    f2 = filter_by_date(mock_sales_df, end_date="2024-01-31")
    assert len(f2) == 2

    # Test Range
    f3 = filter_by_date(mock_sales_df, start_date="2024-01-10", end_date="2024-02-15")
    assert len(f3) == 2

    # Test Out of bounds range
    f4 = filter_by_date(mock_sales_df, start_date="2025-01-01")
    assert len(f4) == 0


def test_get_overview_metrics(mock_sales_df):
    metrics = get_overview_metrics(mock_sales_df)
    assert metrics["total_revenue"] == 3200.0
    assert metrics["total_quantity"] == 41
    assert metrics["total_products"] == 4
    assert metrics["total_records"] == 5
    assert metrics["average_price"] == pytest.approx(96.0, 0.01)
    assert metrics["average_order_value"] == pytest.approx(640.0, 0.01)
    assert metrics["date_range"]["start"] is not None
    assert metrics["date_range"]["end"] is not None


def test_get_overview_metrics_empty():
    empty_df = pd.DataFrame(columns=["date", "product_name", "category", "quantity", "price", "revenue"])
    metrics = get_overview_metrics(empty_df)
    assert metrics["total_revenue"] == 0.0
    assert metrics["total_quantity"] == 0
    assert metrics["total_products"] == 0
    assert metrics["total_records"] == 0
    assert metrics["date_range"]["start"] is None


def test_get_sales_by_product(mock_sales_df):
    # Sort by revenue (default)
    top_rev = get_sales_by_product(mock_sales_df, limit=2, sort_by="revenue")
    assert len(top_rev) == 2
    # Puffer Jacket has 1000 + 200 = 1200, Oxford Shirt has 1000
    assert top_rev[0]["product_name"] == "Puffer Jacket"
    assert top_rev[0]["revenue"] == 1200.0
    assert top_rev[0]["quantity_sold"] == 12

    # Sort by quantity sold
    top_qty = get_sales_by_product(mock_sales_df, limit=2, sort_by="quantity_sold")
    assert top_qty[0]["product_name"] == "Oxford Shirt"
    assert top_qty[0]["quantity_sold"] == 20


def test_get_sales_by_category(mock_sales_df):
    cat_summary = get_sales_by_category(mock_sales_df)
    assert len(cat_summary) == 4
    # Outerwear has 1200, Shirts has 1000, Footwear has 600, Knitwear has 400
    assert cat_summary[0]["category"] == "Outerwear"
    assert cat_summary[0]["revenue"] == 1200.0

    total_pct = sum(c["percentage_of_total"] for c in cat_summary)
    assert pytest.approx(total_pct, 0.1) == 100.0


def test_get_sales_trend(mock_sales_df):
    # Monthly trend
    monthly = get_sales_trend(mock_sales_df, interval="monthly")
    assert len(monthly) == 3
    assert monthly[0]["period"] == "2024-01"
    assert monthly[0]["revenue"] == 1400.0
    assert monthly[1]["period"] == "2024-02"
    assert monthly[1]["revenue"] == 800.0
    assert monthly[2]["period"] == "2024-03"
    assert monthly[2]["revenue"] == 1000.0

    # Daily trend
    daily = get_sales_trend(mock_sales_df, interval="daily")
    assert len(daily) == 5
    assert daily[0]["period"] == "2024-01-01"


def test_get_raw_sales_data(mock_sales_df):
    raw = get_raw_sales_data(mock_sales_df, limit=2, offset=0)
    assert len(raw) == 2
    assert raw[0]["product_name"] == "Puffer Jacket"

    raw_offset = get_raw_sales_data(mock_sales_df, limit=2, offset=3)
    assert len(raw_offset) == 2
    assert raw_offset[0]["product_name"] == "Leather Boots"

    # Out of bounds offset
    raw_empty = get_raw_sales_data(mock_sales_df, limit=10, offset=100)
    assert len(raw_empty) == 0


def test_filter_inverted_dates(mock_sales_df):
    # start_date after end_date should yield empty DataFrame
    res = filter_by_date(mock_sales_df, start_date="2024-03-01", end_date="2024-01-01")
    assert len(res) == 0


def test_empty_dataframe_analytics():
    empty_df = pd.DataFrame(columns=["date", "product_name", "category", "quantity", "price", "revenue"])
    assert get_sales_by_product(empty_df) == []
    assert get_sales_by_category(empty_df) == []
    assert get_sales_trend(empty_df) == []
    assert get_raw_sales_data(empty_df) == []


def test_single_row_metrics():
    single_row = pd.DataFrame([{
        "date": pd.Timestamp("2024-01-01 12:00:00"),
        "product_name": "Trench Coat",
        "category": "Outerwear",
        "quantity": 1,
        "price": 150.0,
        "revenue": 150.0
    }])
    metrics = get_overview_metrics(single_row)
    assert metrics["total_revenue"] == 150.0
    assert metrics["total_quantity"] == 1
    assert metrics["total_products"] == 1
    assert metrics["average_price"] == 150.0
    assert metrics["average_order_value"] == 150.0
