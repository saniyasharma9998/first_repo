"""
data_cleaning.py
----------------
Reusable data-cleaning pipeline for the food-delivery dataset.

Cleaning steps performed:
1.  Load raw CSV
2.  Inspect and fix data types
3.  Remove duplicate records
4.  Handle missing values
5.  Validate and clamp ratings (1-5)
6.  Validate order amounts (>0)
7.  Validate delivery times (>=0)
8.  Handle cancelled orders
9.  Parse date/time columns
10. Detect and cap outliers (IQR method)
11. Create derived/feature-engineered columns
12. Save processed CSV

Run standalone:
    python src/data_cleaning.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAW_PATH       = Path("data/raw/food_delivery_orders.csv")
PROCESSED_PATH = Path("data/processed/cleaned_food_delivery_orders.csv")


# ══════════════════════════════════════════════════════════════════════════════
# Step helpers
# ══════════════════════════════════════════════════════════════════════════════

def load_raw(path: str | Path = RAW_PATH) -> pd.DataFrame:
    """Load raw CSV and return a DataFrame."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Raw data not found at {path}. Run data_generation.py first.")
    df = pd.read_csv(path, low_memory=False)
    print(f"  Loaded {len(df):,} rows × {df.shape[1]} columns from {path}")
    return df


def fix_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Cast columns to appropriate types."""
    df = df.copy()

    # Dates and times
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["order_time"] = pd.to_datetime(
        df["order_date"].astype(str) + " " + df["order_time"].astype(str),
        errors="coerce"
    )

    # Numeric
    numeric_cols = [
        "order_amount", "delivery_fee", "discount",
        "gross_order_value", "final_amount",
        "estimated_delivery_time", "actual_delivery_time",
        "delivery_time_minutes", "customer_rating",
        "number_of_items", "distance_km",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Categorical
    cat_cols = ["cuisine", "city", "area", "payment_method", "order_status"]
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop exact duplicate rows; keep first occurrence."""
    before = len(df)
    df = df.drop_duplicates(subset="order_id", keep="first").reset_index(drop=True)
    after = len(df)
    print(f"  Removed {before - after:,} duplicate rows")
    return df


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Missing-value strategy:
    - customer_rating  : leave NaN for cancelled/unrated — meaningful absence
    - delivery_partner_id : fill with 'UNKNOWN'
    - distance_km      : impute with median by city
    - order_date       : drop (cannot infer)
    """
    df = df.copy()

    # delivery_partner_id
    df["delivery_partner_id"] = df["delivery_partner_id"].fillna("UNKNOWN")

    # distance_km → median by city
    city_median_dist = df.groupby("city")["distance_km"].transform("median")
    df["distance_km"] = df["distance_km"].fillna(city_median_dist)
    # Fallback global median
    global_median = df["distance_km"].median()
    df["distance_km"] = df["distance_km"].fillna(global_median)

    # Drop rows where order_date is unparseable
    before = len(df)
    df = df.dropna(subset=["order_date"])
    dropped = before - len(df)
    if dropped:
        print(f"  Dropped {dropped} rows with unparseable order_date")

    return df


def validate_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """Clamp ratings to [1, 5]; set out-of-range values to NaN."""
    df = df.copy()
    invalid_mask = (df["customer_rating"] < 1) | (df["customer_rating"] > 5)
    n_invalid = invalid_mask.sum()
    if n_invalid:
        print(f"  Set {n_invalid} out-of-range ratings to NaN")
        df.loc[invalid_mask, "customer_rating"] = np.nan
    return df


def validate_amounts(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows where order_amount <= 0 or final_amount < 0."""
    df = df.copy()
    before = len(df)
    df = df[df["order_amount"] > 0]
    df = df[df["final_amount"] >= 0]
    df = df.reset_index(drop=True)
    dropped = before - len(df)
    if dropped:
        print(f"  Dropped {dropped} rows with invalid order amounts")
    return df


def validate_delivery_times(df: pd.DataFrame) -> pd.DataFrame:
    """
    For Delivered/Pending orders, actual_delivery_time must be >= 0.
    Negative values are set to NaN.
    """
    df = df.copy()
    active_mask = df["order_status"].isin(["Delivered", "Pending"])
    neg_mask    = active_mask & (df["actual_delivery_time"] < 0)
    if neg_mask.sum():
        print(f"  Set {neg_mask.sum()} negative delivery times to NaN")
        df.loc[neg_mask, ["actual_delivery_time", "delivery_time_minutes"]] = np.nan
    return df


def cap_outliers(df: pd.DataFrame, cols: list[str], factor: float = 3.0) -> pd.DataFrame:
    """
    Cap outliers using the IQR method (Tukey fences).
    Values beyond median ± factor * IQR are capped.
    """
    df = df.copy()
    for col in cols:
        if col not in df.columns:
            continue
        q1  = df[col].quantile(0.25)
        q3  = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        n_capped = ((df[col] < lower) | (df[col] > upper)).sum()
        if n_capped:
            df[col] = df[col].clip(lower=lower, upper=upper)
            print(f"  Capped {n_capped} outliers in '{col}' to [{lower:.1f}, {upper:.1f}]")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived analytical columns."""
    df = df.copy()

    # ── Date parts ────────────────────────────────────────────────────────────
    df["order_month"]   = df["order_date"].dt.month.astype("Int64")
    df["order_year"]    = df["order_date"].dt.year.astype("Int64")
    df["order_day"]     = df["order_date"].dt.day.astype("Int64")
    df["day_of_week"]   = df["order_date"].dt.dayofweek.astype("Int64")   # Mon=0
    df["order_hour"]    = df["order_time"].dt.hour.astype("Int64")
    df["month_name"]    = df["order_date"].dt.strftime("%b")
    df["day_name"]      = df["order_date"].dt.strftime("%A")
    df["week_number"]   = df["order_date"].dt.isocalendar().week.astype("Int64")
    df["is_weekend"]    = df["day_of_week"].isin([5, 6])

    # ── Revenue aliases ───────────────────────────────────────────────────────
    # net_revenue = final_amount (after discount; excludes cancelled)
    df["net_revenue"] = np.where(
        df["order_status"] == "Delivered",
        df["final_amount"],
        0.0
    )

    # ── Delivery metrics ──────────────────────────────────────────────────────
    df["delivery_delay"] = df["actual_delivery_time"] - df["estimated_delivery_time"]

    def delivery_performance(row):
        if pd.isna(row["delivery_delay"]):
            return "N/A"
        if row["delivery_delay"] <= 0:
            return "Early/On Time"
        if row["delivery_delay"] <= 10:
            return "Slightly Delayed"
        return "Significantly Delayed"

    df["delivery_performance"] = df.apply(delivery_performance, axis=1)
    df["delivery_performance"] = pd.Categorical(
        df["delivery_performance"],
        categories=["Early/On Time", "Slightly Delayed", "Significantly Delayed", "N/A"],
        ordered=False,
    )

    # ── Rating category ───────────────────────────────────────────────────────
    def rate_category(r):
        if pd.isna(r):
            return "Not Rated"
        if r >= 4.5:
            return "Excellent"
        if r >= 3.5:
            return "Good"
        if r >= 2.5:
            return "Average"
        return "Poor"

    df["rating_category"] = df["customer_rating"].apply(rate_category)
    df["rating_category"] = pd.Categorical(
        df["rating_category"],
        categories=["Excellent", "Good", "Average", "Poor", "Not Rated"],
        ordered=False,
    )

    # ── Order-value segment ───────────────────────────────────────────────────
    df["order_value_segment"] = pd.cut(
        df["final_amount"],
        bins=[0, 200, 400, 700, 1_000, np.inf],
        labels=["<₹200", "₹200-400", "₹400-700", "₹700-1K", ">₹1K"],
    )

    # ── Hour bucket ───────────────────────────────────────────────────────────
    def hour_bucket(h):
        if pd.isna(h):
            return "Unknown"
        h = int(h)
        if 6 <= h < 11:
            return "Morning (6-11)"
        if 11 <= h < 15:
            return "Lunch (11-15)"
        if 15 <= h < 18:
            return "Afternoon (15-18)"
        if 18 <= h < 23:
            return "Dinner (18-23)"
        return "Late Night (23-6)"

    df["time_of_day"] = df["order_hour"].apply(hour_bucket)

    return df


# ══════════════════════════════════════════════════════════════════════════════
# Public pipeline
# ══════════════════════════════════════════════════════════════════════════════

def run_cleaning_pipeline(
    raw_path: str | Path = RAW_PATH,
    output_path: str | Path = PROCESSED_PATH,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Execute the full data-cleaning pipeline.

    Parameters
    ----------
    raw_path    : path to raw CSV
    output_path : path to save cleaned CSV
    verbose     : print step-level messages

    Returns
    -------
    pd.DataFrame  cleaned dataset
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if verbose:
        print("\n── Step 1: Load raw data ──────────────────────────────────")
    df = load_raw(raw_path)

    if verbose:
        print("\n── Step 2: Fix data types ─────────────────────────────────")
    df = fix_dtypes(df)

    if verbose:
        print("\n── Step 3: Remove duplicates ──────────────────────────────")
    df = remove_duplicates(df)

    if verbose:
        print("\n── Step 4: Handle missing values ──────────────────────────")
    df = handle_missing(df)

    if verbose:
        print("\n── Step 5: Validate ratings ───────────────────────────────")
    df = validate_ratings(df)

    if verbose:
        print("\n── Step 6: Validate order amounts ─────────────────────────")
    df = validate_amounts(df)

    if verbose:
        print("\n── Step 7: Validate delivery times ────────────────────────")
    df = validate_delivery_times(df)

    if verbose:
        print("\n── Step 8: Cap outliers ────────────────────────────────────")
    df = cap_outliers(
        df,
        cols=["order_amount", "final_amount", "delivery_time_minutes", "distance_km"],
        factor=3.0,
    )

    if verbose:
        print("\n── Step 9: Engineer features ───────────────────────────────")
    df = engineer_features(df)

    # Preserve order
    df = df.sort_values("order_date").reset_index(drop=True)

    df.to_csv(output_path, index=False)
    if verbose:
        print(f"\n✓  Cleaned dataset saved → {output_path}")
        print(f"   Final shape: {df.shape[0]:,} rows × {df.shape[1]} columns")

    return df


if __name__ == "__main__":
    run_cleaning_pipeline()
