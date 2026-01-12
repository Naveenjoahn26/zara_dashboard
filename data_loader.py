import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "zara.csv"


def load_and_clean_sales_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"CSV not found at {DATA_PATH}")

    # Zara CSV uses semicolon separator
    df = pd.read_csv(DATA_PATH, sep=";")

    print("CSV SHAPE:", df.shape)
    print("RAW COLUMNS:", df.columns.tolist())

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

    print("NORMALIZED COLUMNS:", df.columns.tolist())

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
    df["revenue"] = df["price"] * df["quantity"]

    df = df.drop_duplicates()

    # 🔒 GUARANTEED RETURN
    return df[
        ["date", "product_name", "category", "quantity", "price", "revenue"]
    ]
