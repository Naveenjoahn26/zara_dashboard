import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "sales-analytics-api"
    assert "version" in data
    assert "total_records" in data


def test_overview_endpoint(client):
    res = client.get("/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert "total_revenue" in data
    assert "total_quantity" in data
    assert "total_products" in data
    assert "average_price" in data
    assert data["total_revenue"] >= 0


def test_overview_date_filtering(client):
    res = client.get("/analytics/overview?start_date=2024-01-01&end_date=2024-02-01")
    assert res.status_code == 200
    data = res.json()
    assert "total_revenue" in data


def test_sales_by_product_endpoint(client):
    res = client.get("/analytics/sales-by-product?limit=5&sort_by=revenue")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) <= 5
    if len(data) > 0:
        assert "product_name" in data[0]
        assert "revenue" in data[0]
        assert "quantity_sold" in data[0]


def test_sales_by_product_invalid_sort(client):
    res = client.get("/analytics/sales-by-product?sort_by=invalid_col")
    assert res.status_code == 422  # validation error


def test_sales_by_category_endpoint(client):
    res = client.get("/analytics/sales-by-category")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "category" in data[0]
        assert "percentage_of_total" in data[0]


def test_sales_trend_endpoint(client):
    # Monthly
    res_m = client.get("/analytics/sales-trend?interval=monthly")
    assert res_m.status_code == 200
    data_m = res_m.json()
    assert isinstance(data_m, list)
    if len(data_m) > 0:
        assert "period" in data_m[0]
        assert "revenue" in data_m[0]

    # Daily
    res_d = client.get("/analytics/sales-trend?interval=daily")
    assert res_d.status_code == 200
    data_d = res_d.json()
    assert isinstance(data_d, list)


def test_sales_trend_invalid_interval(client):
    res = client.get("/analytics/sales-trend?interval=yearly")
    assert res.status_code == 422  # regex validation fails


def test_raw_sales_endpoint(client):
    res = client.get("/analytics/raw-sales?limit=10&offset=0")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) <= 10
    if len(data) > 0:
        assert "product_name" in data[0]
        assert "price" in data[0]
        assert "revenue" in data[0]


def test_raw_sales_out_of_bounds_404(client):
    res = client.get("/analytics/raw-sales?limit=50&offset=99999999")
    assert res.status_code == 404
    assert res.json()["detail"] == "No data found"


def test_filters_endpoint(client):
    res = client.get("/analytics/filters")
    assert res.status_code == 200
    data = res.json()
    assert "categories" in data
    assert "date_range" in data
    assert "total_records" in data


def test_datasets_management_and_switch(client):
    res_list = client.get("/analytics/datasets")
    assert res_list.status_code == 200
    datasets = res_list.json()["available_datasets"]
    assert "zara.csv" in datasets

    # Switch to zara.csv
    res_switch = client.post("/analytics/switch-dataset", json={"dataset_name": "zara.csv"})
    assert res_switch.status_code == 200
    assert res_switch.json()["active_dataset"] == "zara.csv"

    # Switch to non-existent dataset
    res_fail = client.post("/analytics/switch-dataset", json={"dataset_name": "non_existent.csv"})
    assert res_fail.status_code == 404


def test_sales_by_product_limit_boundaries(client):
    # ge=1, le=50
    res_zero = client.get("/analytics/sales-by-product?limit=0")
    assert res_zero.status_code == 422

    res_too_large = client.get("/analytics/sales-by-product?limit=100")
    assert res_too_large.status_code == 422


def test_raw_sales_limit_boundaries(client):
    # ge=1, le=100
    res_zero = client.get("/analytics/raw-sales?limit=0")
    assert res_zero.status_code == 422

    res_negative_offset = client.get("/analytics/raw-sales?offset=-5")
    assert res_negative_offset.status_code == 422
