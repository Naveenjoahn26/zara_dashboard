import pandas as pd
from typing import Optional, List, Dict, Any


def filter_by_date(
    df: pd.DataFrame,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """Filter dataframe by start_date and end_date (inclusive)."""
    if df.empty:
        return df.copy()

    filtered = df.copy()

    if start_date:
        parsed_start = pd.to_datetime(start_date, errors="coerce")
        if pd.notna(parsed_start):
            filtered = filtered[filtered["date"] >= parsed_start]

    if end_date:
        parsed_end = pd.to_datetime(end_date, errors="coerce")
        if pd.notna(parsed_end):
            # If end_date has no time specified (e.g. 2024-02-19), extend to end of day
            if parsed_end.time() == pd.Timestamp("00:00:00").time():
                parsed_end = parsed_end + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
            filtered = filtered[filtered["date"] <= parsed_end]

    return filtered


def get_overview_metrics(
    df: pd.DataFrame,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Calculate high-level KPI overview metrics."""
    filtered = filter_by_date(df, start_date, end_date)

    if filtered.empty:
        return {
            "total_revenue": 0.0,
            "total_quantity": 0,
            "total_products": 0,
            "average_price": 0.0,
            "average_order_value": 0.0,
            "total_records": 0,
            "date_range": {
                "start": None,
                "end": None
            }
        }

    total_revenue = float(filtered["revenue"].sum())
    total_quantity = int(filtered["quantity"].sum())
    total_products = int(filtered["product_name"].nunique())
    avg_price = float(filtered["price"].mean())
    avg_order_value = float(total_revenue / len(filtered)) if len(filtered) > 0 else 0.0

    min_date = filtered["date"].min()
    max_date = filtered["date"].max()

    return {
        "total_revenue": round(total_revenue, 2),
        "total_quantity": total_quantity,
        "total_products": total_products,
        "average_price": round(avg_price, 2),
        "average_order_value": round(avg_order_value, 2),
        "total_records": len(filtered),
        "date_range": {
            "start": min_date.isoformat() if pd.notna(min_date) else None,
            "end": max_date.isoformat() if pd.notna(max_date) else None
        }
    }


def get_sales_by_product(
    df: pd.DataFrame,
    limit: int = 10,
    sort_by: str = "revenue",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get sales performance aggregated by product."""
    filtered = filter_by_date(df, start_date, end_date)

    if filtered.empty:
        return []

    agg_df = filtered.groupby("product_name").agg(
        revenue=("revenue", "sum"),
        quantity_sold=("quantity", "sum"),
        average_price=("price", "mean")
    ).reset_index()

    sort_col = "quantity_sold" if sort_by == "quantity_sold" else "revenue"
    agg_df = agg_df.sort_values(by=sort_col, ascending=False).head(limit)

    agg_df["revenue"] = agg_df["revenue"].round(2)
    agg_df["average_price"] = agg_df["average_price"].round(2)
    agg_df["quantity_sold"] = agg_df["quantity_sold"].astype(int)

    return agg_df.to_dict(orient="records")


def get_sales_by_category(
    df: pd.DataFrame,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get sales breakdown by category."""
    filtered = filter_by_date(df, start_date, end_date)

    if filtered.empty:
        return []

    agg_df = filtered.groupby("category").agg(
        revenue=("revenue", "sum"),
        quantity_sold=("quantity", "sum"),
        product_count=("product_name", "nunique")
    ).reset_index()

    total_revenue = agg_df["revenue"].sum()
    if total_revenue > 0:
        agg_df["percentage_of_total"] = (agg_df["revenue"] / total_revenue * 100).round(2)
    else:
        agg_df["percentage_of_total"] = 0.0

    agg_df = agg_df.sort_values(by="revenue", ascending=False)
    agg_df["revenue"] = agg_df["revenue"].round(2)
    agg_df["quantity_sold"] = agg_df["quantity_sold"].astype(int)
    agg_df["product_count"] = agg_df["product_count"].astype(int)

    return agg_df.to_dict(orient="records")


def get_sales_trend(
    df: pd.DataFrame,
    interval: str = "monthly",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get sales trend over time (daily or monthly)."""
    filtered = filter_by_date(df, start_date, end_date)

    if filtered.empty:
        return []

    trend_df = filtered.copy()

    if interval == "daily":
        trend_df["period"] = trend_df["date"].dt.strftime("%Y-%m-%d")
    else:  # monthly
        trend_df["period"] = trend_df["date"].dt.strftime("%Y-%m")

    agg_df = trend_df.groupby("period").agg(
        revenue=("revenue", "sum"),
        quantity_sold=("quantity", "sum"),
        order_count=("product_name", "count")
    ).reset_index().sort_values(by="period")

    agg_df["revenue"] = agg_df["revenue"].round(2)
    agg_df["quantity_sold"] = agg_df["quantity_sold"].astype(int)
    agg_df["order_count"] = agg_df["order_count"].astype(int)

    return agg_df.to_dict(orient="records")


def get_raw_sales_data(
    df: pd.DataFrame,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Return paginated raw sales records."""
    if df.empty or offset >= len(df):
        return []

    slice_df = df.iloc[offset : offset + limit].copy()

    # Convert date to string format
    slice_df["date"] = slice_df["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    slice_df["revenue"] = slice_df["revenue"].round(2)
    slice_df["price"] = slice_df["price"].round(2)
    slice_df["quantity"] = slice_df["quantity"].astype(int)

    return slice_df.to_dict(orient="records")

