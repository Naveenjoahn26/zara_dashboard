import os
from pathlib import Path
from typing import Optional, Union
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = BASE_DIR / "zara.csv"


def detect_separator(file_path: Path) -> str:
    """Detect whether CSV uses semicolon or comma delimiter."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            header_sample = f.readline()
            semicolon_count = header_sample.count(";")
            comma_count = header_sample.count(",")
            return ";" if semicolon_count > comma_count else ","
    except Exception:
        return ";"


def load_and_clean_sales_data(data_path: Optional[Union[Path, str]] = None) -> pd.DataFrame:
    """
    Load, normalize, clean, and enrich sales data.
    Supports both Zara's semicolon CSV format and standard CSV datasets.
    """
    if data_path:
        target_path = Path(data_path)
    else:
        env_path = os.getenv("SALES_DATA_PATH")
        if env_path and Path(env_path).exists():
            target_path = Path(env_path)
        elif DEFAULT_DATA_PATH.exists():
            target_path = DEFAULT_DATA_PATH
        else:
            sample_path = BASE_DIR / "sample_sales_data.csv"
            if sample_path.exists():
                target_path = sample_path
            else:
                raise FileNotFoundError(f"Neither {DEFAULT_DATA_PATH} nor sample data found")

    if not target_path.exists():
        raise FileNotFoundError(f"CSV not found at {target_path}")

    sep = detect_separator(target_path)
    df = pd.read_csv(target_path, sep=sep)

    if df.empty:
        raise ValueError("CSV loaded but contains no rows")

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Rename to analytics schema
    df = df.rename(columns={
        "name": "product_name",
        "product_category": "category",
        "sales_volume": "quantity",
        "scraped_at": "date",
    })

    # If dataset has uniform category but diverse terms (like original Zara CSV), enrich category
    if "terms" in df.columns and "category" in df.columns:
        if df["category"].nunique() <= 1 and df["terms"].nunique() > 1:
            df["category"] = df["terms"].astype(str).str.strip().str.title()

    required_columns = {
        "product_name", "category", "quantity", "price", "date"
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Cleaning
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "product_name", "category"])

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

    # Derived revenue
    if "revenue" not in df.columns:
        df["revenue"] = df["price"] * df["quantity"]
    else:
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(df["price"] * df["quantity"])

    df = df.drop_duplicates()

    # Sort by date for chronological consistency
    df = df.sort_values(by="date").reset_index(drop=True)

    # Guaranteed return schema
    return df[
        ["date", "product_name", "category", "quantity", "price", "revenue"]
    ]
