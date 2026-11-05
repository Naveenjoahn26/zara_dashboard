import pytest
import pandas as pd
from pathlib import Path
import tempfile

from generate_sample_data import generate_sales_dataset, CATEGORIES


def test_generate_sample_dataset():
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as tmp:
        tmp_path = Path(tmp.name)

    try:
        output_path = generate_sales_dataset(num_records=100, output_path=tmp_path)
        assert output_path.exists()

        # Check content with pandas
        df = pd.read_csv(output_path, sep=";")
        assert len(df) == 100
        assert "Product ID" in df.columns
        assert "Sales Volume" in df.columns
        assert "price" in df.columns
        assert "scraped_at" in df.columns
        assert "Product Category" in df.columns

        # Verify prices and volumes are positive
        assert (df["price"] > 0).all()
        assert (df["Sales Volume"] > 0).all()

        # Verify categories match defined categories
        assert set(df["Product Category"].unique()).issubset(set(CATEGORIES.keys()))

    finally:
        tmp_path.unlink(missing_ok=True)

