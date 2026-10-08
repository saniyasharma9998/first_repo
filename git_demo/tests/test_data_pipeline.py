"""
tests/test_data_pipeline.py
----------------------------
Automated tests for the food-delivery analytics data pipeline.

Run:
    pytest tests/ -v
or:
    pytest tests/ -v --tb=short
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# ── Make src/ importable ──────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

RAW_PATH       = Path("data/raw/food_delivery_orders.csv")
PROCESSED_PATH = Path("data/processed/cleaned_food_delivery_orders.csv")

# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def raw_df() -> pd.DataFrame:
    """Load raw dataset once for all tests in this module."""
    if not RAW_PATH.exists():
        pytest.skip(f"Raw data not found at {RAW_PATH}. Run data_generation.py first.")
    return pd.read_csv(RAW_PATH, low_memory=False)


@pytest.fixture(scope="module")
def clean_df() -> pd.DataFrame:
    """Load processed dataset once for all tests in this module."""
    if not PROCESSED_PATH.exists():
        pytest.skip(f"Processed data not found at {PROCESSED_PATH}. Run data_cleaning.py first.")
    df = pd.read_csv(PROCESSED_PATH, low_memory=False, parse_dates=["order_date"])
    for col in ["order_amount", "final_amount", "customer_rating",
                "delivery_time_minutes", "delivery_delay", "distance_km"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Raw Dataset
# ═══════════════════════════════════════════════════════════════════════════════

class TestRawDataset:
    """Validate the raw dataset file and its basic structure."""

    def test_raw_file_exists(self):
        """Raw CSV file must exist."""
        assert RAW_PATH.exists(), f"Missing: {RAW_PATH}"

    def test_raw_minimum_rows(self, raw_df):
        """Raw dataset must have at least 10,000 rows."""
        assert len(raw_df) >= 10_000, f"Only {len(raw_df)} rows — expected ≥ 10,000"

    def test_raw_required_columns(self, raw_df):
        """All required raw columns must be present."""
        required = [
            "order_id", "order_date", "order_time", "customer_id",
            "restaurant_id", "restaurant_name", "cuisine", "city", "area",
            "order_amount", "delivery_fee", "discount",
            "gross_order_value", "final_amount", "payment_method",
            "order_status", "delivery_partner_id",
            "estimated_delivery_time", "actual_delivery_time",
            "delivery_time_minutes", "customer_rating",
            "number_of_items", "distance_km",
        ]
        missing = [c for c in required if c not in raw_df.columns]
        assert not missing, f"Missing columns: {missing}"

    def test_raw_order_id_format(self, raw_df):
        """Order IDs must follow ORD###### pattern."""
        sample = raw_df["order_id"].dropna().head(100)
        assert sample.str.startswith("ORD").all(), "Order IDs should start with 'ORD'"

    def test_raw_order_status_values(self, raw_df):
        """order_status must only contain expected values."""
        allowed = {"Delivered", "Cancelled", "Pending"}
        actual  = set(raw_df["order_status"].dropna().unique())
        unexpected = actual - allowed
        assert not unexpected, f"Unexpected order_status values: {unexpected}"

    def test_raw_city_values(self, raw_df):
        """City column must contain only the 6 expected cities."""
        expected = {"Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Pune"}
        actual   = set(raw_df["city"].dropna().unique())
        unexpected = actual - expected
        assert not unexpected, f"Unexpected city values: {unexpected}"

    def test_raw_ratings_range(self, raw_df):
        """All non-null ratings must be in [1.0, 5.0]."""
        ratings = pd.to_numeric(raw_df["customer_rating"], errors="coerce").dropna()
        assert (ratings >= 1.0).all(), "Some ratings are below 1.0"
        assert (ratings <= 5.0).all(), "Some ratings are above 5.0"

    def test_raw_order_amounts_positive(self, raw_df):
        """order_amount must be positive for all rows."""
        amounts = pd.to_numeric(raw_df["order_amount"], errors="coerce").dropna()
        assert (amounts > 0).all(), "Some order_amount values are zero or negative"

    def test_raw_delivery_fee_nonnegative(self, raw_df):
        """delivery_fee must be ≥ 0."""
        fees = pd.to_numeric(raw_df["delivery_fee"], errors="coerce").dropna()
        assert (fees >= 0).all(), "Some delivery_fee values are negative"

    def test_raw_discount_nonnegative(self, raw_df):
        """discount must be ≥ 0."""
        discounts = pd.to_numeric(raw_df["discount"], errors="coerce").dropna()
        assert (discounts >= 0).all(), "Some discount values are negative"

    def test_raw_number_of_items_positive(self, raw_df):
        """number_of_items must be ≥ 1."""
        items = pd.to_numeric(raw_df["number_of_items"], errors="coerce").dropna()
        assert (items >= 1).all(), "Some number_of_items values are < 1"

    def test_raw_distance_positive(self, raw_df):
        """Non-null distance_km must be > 0."""
        dist = pd.to_numeric(raw_df["distance_km"], errors="coerce").dropna()
        assert (dist > 0).all(), "Some distance_km values are zero or negative"

    def test_raw_gross_order_value_consistency(self, raw_df):
        """gross_order_value ≈ order_amount + delivery_fee (within ₹1 tolerance)."""
        df = raw_df.copy()
        for c in ["order_amount", "delivery_fee", "gross_order_value"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        diff = (df["gross_order_value"] - (df["order_amount"] + df["delivery_fee"])).abs()
        assert (diff.dropna() < 1.0).all(), "gross_order_value ≠ order_amount + delivery_fee"

    def test_raw_final_amount_consistency(self, raw_df):
        """final_amount ≈ gross_order_value − discount (within ₹1 tolerance)."""
        df = raw_df.copy()
        for c in ["gross_order_value", "discount", "final_amount"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        diff = (df["final_amount"] - (df["gross_order_value"] - df["discount"])).abs()
        assert (diff.dropna() < 1.0).all(), "final_amount ≠ gross_order_value − discount"

    def test_raw_has_controlled_missing_values(self, raw_df):
        """Dataset should have some missing values (intentional for cleaning demo)."""
        total_nulls = raw_df.isnull().sum().sum()
        assert total_nulls > 0, "Dataset has no missing values — cleaning demo won't work"

    def test_raw_has_duplicates(self, raw_df):
        """Dataset should have some duplicate order_ids (intentional)."""
        dup_count = raw_df.duplicated(subset="order_id").sum()
        assert dup_count > 0, "Dataset has no duplicate order_ids — cleaning demo won't work"


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Processed (Cleaned) Dataset
# ═══════════════════════════════════════════════════════════════════════════════

class TestProcessedDataset:
    """Validate the cleaned and feature-engineered dataset."""

    def test_processed_file_exists(self):
        """Processed CSV file must exist."""
        assert PROCESSED_PATH.exists(), f"Missing: {PROCESSED_PATH}"

    def test_processed_has_fewer_rows_than_raw(self, raw_df, clean_df):
        """Cleaning should remove duplicates, so processed < raw."""
        assert len(clean_df) < len(raw_df), "Cleaning did not remove any rows"

    def test_processed_no_duplicate_order_ids(self, clean_df):
        """Processed dataset must have no duplicate order_ids."""
        dups = clean_df.duplicated(subset="order_id").sum()
        assert dups == 0, f"Processed dataset has {dups} duplicate order_ids"

    def test_processed_required_raw_columns(self, clean_df):
        """All original raw columns should be preserved."""
        required = [
            "order_id", "order_date", "customer_id", "restaurant_id",
            "order_amount", "final_amount", "order_status", "customer_rating",
            "delivery_time_minutes", "distance_km",
        ]
        missing = [c for c in required if c not in clean_df.columns]
        assert not missing, f"Missing raw columns in processed data: {missing}"

    def test_processed_engineered_columns(self, clean_df):
        """Feature-engineered columns must be present."""
        engineered = [
            "order_month", "order_year", "day_of_week", "order_hour",
            "month_name", "day_name", "is_weekend", "net_revenue",
            "delivery_delay", "delivery_performance", "rating_category",
            "time_of_day",
        ]
        missing = [c for c in engineered if c not in clean_df.columns]
        assert not missing, f"Missing engineered columns: {missing}"

    def test_processed_ratings_range(self, clean_df):
        """All non-null ratings in processed data must be in [1.0, 5.0]."""
        ratings = clean_df["customer_rating"].dropna()
        assert (ratings >= 1.0).all(), "Processed ratings contain values < 1.0"
        assert (ratings <= 5.0).all(), "Processed ratings contain values > 5.0"

    def test_processed_order_amounts_positive(self, clean_df):
        """order_amount must be positive."""
        assert (clean_df["order_amount"] > 0).all(), "order_amount has non-positive values"

    def test_processed_final_amount_nonnegative(self, clean_df):
        """final_amount must be ≥ 0."""
        assert (clean_df["final_amount"] >= 0).all(), "final_amount has negative values"

    def test_processed_delivery_time_nonnegative(self, clean_df):
        """Non-null delivery times must be ≥ 0."""
        dt = clean_df["delivery_time_minutes"].dropna()
        assert (dt >= 0).all(), "delivery_time_minutes has negative values"

    def test_processed_net_revenue_nonnegative(self, clean_df):
        """net_revenue must be ≥ 0 (0 for cancelled orders)."""
        assert (clean_df["net_revenue"] >= 0).all(), "net_revenue has negative values"

    def test_processed_net_revenue_zero_for_cancelled(self, clean_df):
        """net_revenue must be 0 for cancelled orders."""
        cancelled_rev = clean_df.loc[clean_df["order_status"] == "Cancelled", "net_revenue"]
        assert (cancelled_rev == 0).all(), "Cancelled orders have non-zero net_revenue"

    def test_processed_distance_nonnull_after_imputation(self, clean_df):
        """distance_km should have no nulls after imputation."""
        nulls = clean_df["distance_km"].isnull().sum()
        assert nulls == 0, f"distance_km still has {nulls} null values after imputation"

    def test_processed_delivery_partner_no_nulls(self, clean_df):
        """delivery_partner_id should have no nulls after filling."""
        nulls = clean_df["delivery_partner_id"].isnull().sum()
        assert nulls == 0, f"delivery_partner_id still has {nulls} null values"

    def test_processed_order_date_parsed(self, clean_df):
        """order_date should be datetime type."""
        assert pd.api.types.is_datetime64_any_dtype(clean_df["order_date"]), \
            "order_date is not datetime type"

    def test_processed_delivery_delay_calculation(self, clean_df):
        """delivery_delay = actual_delivery_time − estimated_delivery_time."""
        delivered = clean_df[clean_df["order_status"] == "Delivered"].dropna(
            subset=["actual_delivery_time", "estimated_delivery_time", "delivery_delay"]
        )
        computed_delay = delivered["actual_delivery_time"] - delivered["estimated_delivery_time"]
        diff = (delivered["delivery_delay"] - computed_delay).abs()
        assert (diff < 0.01).all(), "delivery_delay calculation is incorrect"

    def test_processed_is_weekend_correct(self, clean_df):
        """is_weekend must be True for Saturday/Sunday only."""
        weekend_days  = clean_df[clean_df["is_weekend"] == True]["day_name"].unique()
        weekday_days  = clean_df[clean_df["is_weekend"] == False]["day_name"].unique()
        for d in weekend_days:
            assert d in ["Saturday", "Sunday"], f"Non-weekend day {d} marked as weekend"
        for d in weekday_days:
            assert d not in ["Saturday", "Sunday"], f"Weekend day {d} marked as weekday"


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Analysis Functions
# ═══════════════════════════════════════════════════════════════════════════════

class TestAnalysisFunctions:
    """Test the core analysis module."""

    def test_all_kpis_return_dict(self, clean_df):
        from src.analysis import all_kpis
        kpis = all_kpis(clean_df)
        expected_keys = [
            "total_orders", "completed_orders", "total_revenue",
            "avg_order_value", "avg_rating", "avg_delivery_time",
            "on_time_pct", "cancellation_rate",
        ]
        for k in expected_keys:
            assert k in kpis, f"KPI '{k}' missing from all_kpis()"

    def test_total_orders_equals_row_count(self, clean_df):
        from src.analysis import kpi_total_orders
        assert kpi_total_orders(clean_df) == len(clean_df)

    def test_completed_orders_less_than_total(self, clean_df):
        from src.analysis import kpi_total_orders, kpi_completed_orders
        assert kpi_completed_orders(clean_df) <= kpi_total_orders(clean_df)

    def test_total_revenue_positive(self, clean_df):
        from src.analysis import kpi_total_revenue
        assert kpi_total_revenue(clean_df) > 0

    def test_avg_rating_in_range(self, clean_df):
        from src.analysis import kpi_avg_rating
        r = kpi_avg_rating(clean_df)
        assert 1.0 <= r <= 5.0, f"Avg rating {r} out of [1, 5]"

    def test_on_time_pct_in_range(self, clean_df):
        from src.analysis import kpi_on_time_pct
        pct = kpi_on_time_pct(clean_df)
        assert 0.0 <= pct <= 100.0, f"On-time % {pct} out of [0, 100]"

    def test_cancellation_rate_in_range(self, clean_df):
        from src.analysis import kpi_cancellation_rate
        rate = kpi_cancellation_rate(clean_df)
        assert 0.0 <= rate <= 100.0, f"Cancellation rate {rate} out of [0, 100]"

    def test_orders_by_month_has_12_months(self, clean_df):
        from src.analysis import orders_by_month
        result = orders_by_month(clean_df)
        assert len(result) == 12, f"Expected 12 months, got {len(result)}"

    def test_top_restaurants_revenue_count(self, clean_df):
        from src.analysis import top_restaurants_revenue
        result = top_restaurants_revenue(clean_df, n=10)
        assert len(result) <= 10

    def test_restaurant_performance_score_range(self, clean_df):
        from src.analysis import restaurant_performance_score
        result = restaurant_performance_score(clean_df)
        if len(result) > 0:
            assert result["performance_score"].between(0, 1).all(), \
                "Performance scores outside [0, 1]"

    def test_correlation_matrix_is_square(self, clean_df):
        from src.analysis import correlation_matrix
        corr = correlation_matrix(clean_df)
        assert corr.shape[0] == corr.shape[1], "Correlation matrix is not square"

    def test_correlation_diagonal_is_one(self, clean_df):
        from src.analysis import correlation_matrix
        corr = correlation_matrix(clean_df)
        diag = np.diag(corr.values)
        assert np.allclose(diag, 1.0, atol=1e-6), "Diagonal of correlation matrix ≠ 1"


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Data Generation (integration)
# ═══════════════════════════════════════════════════════════════════════════════

class TestDataGeneration:
    """Test the data generation module."""

    def test_generator_imports(self):
        from src.data_generation import generate_dataset
        assert callable(generate_dataset)

    def test_cleaning_pipeline_imports(self):
        from src.data_cleaning import run_cleaning_pipeline
        assert callable(run_cleaning_pipeline)

    def test_utils_fmt_inr(self):
        from src.utils import fmt_inr
        assert fmt_inr(1_234_567) == "₹1.2M"
        assert fmt_inr(54_000) == "₹54.0K"
        assert fmt_inr(999) == "₹999"

    def test_utils_normalize_series(self):
        from src.utils import normalize_series
        s = pd.Series([0.0, 5.0, 10.0])
        norm = normalize_series(s)
        assert norm.min() == pytest.approx(0.0)
        assert norm.max() == pytest.approx(1.0)
