import pytest
import pandas as pd
from pathlib import Path
import tempfile

from data_loader import (
    load_and_clean_sales_data,
    detect_separator,
    BASE_DIR,
    DEFAULT_DATA_PATH
)


def test_detect_separator():
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as f_semi:
        f_semi.write("col1;col2;col3\n1;2;3\n")
        semi_path = Path(f_semi.name)

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as f_comma:
        f_comma.write("col1,col2,col3\n1,2,3\n")
        comma_path = Path(f_comma.name)

    try:
        assert detect_separator(semi_path) == ";"
        assert detect_separator(comma_path) == ","
    finally:
        semi_path.unlink(missing_ok=True)
        comma_path.unlink(missing_ok=True)


def test_load_and_clean_zara_data():
    if DEFAULT_DATA_PATH.exists():
        df = load_and_clean_sales_data(DEFAULT_DATA_PATH)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert set(df.columns) == {
            "date", "product_name", "category", "quantity", "price", "revenue"
        }
        assert (df["revenue"] == df["price"] * df["quantity"]).all()
        assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_load_and_clean_sample_data():
    sample_path = BASE_DIR / "sample_sales_data.csv"
    if sample_path.exists():
        df = load_and_clean_sales_data(sample_path)
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 1000
        assert df["category"].nunique() > 1
        assert (df["revenue"] >= 0).all()
        assert (df["quantity"] >= 0).all()


def test_load_missing_file_raises_error():
    with pytest.raises(FileNotFoundError):
        load_and_clean_sales_data(BASE_DIR / "non_existent_file_xyz.csv")


def test_load_empty_csv_raises_error():
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as f:
        f.write("")
        tmp_path = Path(f.name)

    try:
        with pytest.raises(Exception):
            load_and_clean_sales_data(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def test_load_missing_required_columns():
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as f:
        f.write("name;price\nItem A;10.5\n")
        tmp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="Missing required columns"):
            load_and_clean_sales_data(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

