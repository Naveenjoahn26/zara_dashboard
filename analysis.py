"""
Legacy / Exploratory analysis helper module.
Delegates to high-performance data_loader and analytics engines.
"""
import pandas as pd
from data_loader import load_and_clean_sales_data


def load_data(path: str = None) -> pd.DataFrame:
    """Load cleaned sales dataframe."""
    return load_and_clean_sales_data(path)


if __name__ == "__main__":
    df = load_data()
    print("Dataset Summary:")
    print(df.info())
    print("\nHead:")
    print(df.head())
