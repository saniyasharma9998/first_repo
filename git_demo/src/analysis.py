"""
analysis.py
-----------
Core analytics functions used by both notebooks and the Streamlit dashboard.

All functions accept a cleaned DataFrame and return either a DataFrame
(for tables/charts) or a scalar (for KPI cards).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils import normalize_series


# ══════════════════════════════════════════════════════════════════════════════
# KPI helpers
# ══════════════════════════════════════════════════════════════════════════════

def kpi_total_orders(df: pd.DataFrame) -> int:
    return len(df)


def kpi_completed_orders(df: pd.DataFrame) -> int:
    return int((df["order_status"] == "Delivered").sum())


def kpi_total_revenue(df: pd.DataFrame) -> float:
    """Sum of final_amount for Delivered orders."""
    return float(df.loc[df["order_status"] == "Delivered", "final_amount"].sum())


def kpi_avg_order_value(df: pd.DataFrame) -> float:
    return float(df.loc[df["order_status"] == "Delivered", "final_amount"].mean())


def kpi_avg_rating(df: pd.DataFrame) -> float:
    return float(df["customer_rating"].mean())


def kpi_avg_delivery_time(df: pd.DataFrame) -> float:
    return float(df.loc[df["order_status"] == "Delivered", "delivery_time_minutes"].mean())


def kpi_on_time_pct(df: pd.DataFrame) -> float:
    """Percentage of delivered orders with delivery_delay <= 0."""
    delivered = df[df["order_status"] == "Delivered"].copy()
    if len(delivered) == 0:
        return 0.0
    on_time = (delivered["delivery_delay"] <= 0).sum()
    return float(on_time / len(delivered) * 100)


def kpi_cancellation_rate(df: pd.DataFrame) -> float:
    if len(df) == 0:
        return 0.0
    cancelled = (df["order_status"] == "Cancelled").sum()
    return float(cancelled / len(df) * 100)


def all_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Return all KPIs as a dictionary."""
    return {
        "total_orders":       kpi_total_orders(df),
        "completed_orders":   kpi_completed_orders(df),
        "total_revenue":      kpi_total_revenue(df),
        "avg_order_value":    kpi_avg_order_value(df),
        "avg_rating":         kpi_avg_rating(df),
        "avg_delivery_time":  kpi_avg_delivery_time(df),
        "on_time_pct":        kpi_on_time_pct(df),
        "cancellation_rate":  kpi_cancellation_rate(df),
    }


# ══════════════════════════════════════════════════════════════════════════════
# Orders analysis
# ══════════════════════════════════════════════════════════════════════════════

def orders_over_time(df: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
    """Aggregate order count and revenue by time period."""
    delivered = df[df["order_status"] == "Delivered"].copy()
    grp = delivered.set_index("order_date").resample(freq).agg(
        orders=("order_id", "count"),
        revenue=("final_amount", "sum"),
        avg_order_value=("final_amount", "mean"),
    ).reset_index()
    grp.columns = ["date", "orders", "revenue", "avg_order_value"]
    return grp


def orders_by_month(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("month_name", observed=True).agg(
        orders=("order_id", "count"),
        revenue=("final_amount", "sum"),
    ).reset_index()
    # Sort by calendar month
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    grp["month_name"] = pd.Categorical(grp["month_name"], categories=month_order, ordered=True)
    return grp.sort_values("month_name").reset_index(drop=True)


def orders_by_day(df: pd.DataFrame) -> pd.DataFrame:
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    grp = df.groupby("day_name", observed=True).agg(
        orders=("order_id", "count"),
        avg_revenue=("final_amount", "mean"),
    ).reset_index()
    grp["day_name"] = pd.Categorical(grp["day_name"], categories=day_order, ordered=True)
    return grp.sort_values("day_name").reset_index(drop=True)


def orders_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("order_hour", observed=True).agg(
        orders=("order_id", "count"),
    ).reset_index()
    return grp.sort_values("order_hour")


def orders_by_cuisine(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("cuisine", observed=True).agg(
        orders=("order_id", "count"),
        revenue=("final_amount", "sum"),
        avg_rating=("customer_rating", "mean"),
    ).reset_index()
    return grp.sort_values("orders", ascending=False).reset_index(drop=True)


def orders_by_city(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("city", observed=True).agg(
        orders=("order_id", "count"),
        revenue=("final_amount", "sum"),
        avg_rating=("customer_rating", "mean"),
        avg_delivery_time=("delivery_time_minutes", "mean"),
    ).reset_index()
    return grp.sort_values("revenue", ascending=False).reset_index(drop=True)


def order_status_distribution(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("order_status", observed=True).agg(
        count=("order_id", "count"),
    ).reset_index()
    grp["pct"] = grp["count"] / grp["count"].sum() * 100
    return grp


# ══════════════════════════════════════════════════════════════════════════════
# Restaurant analysis
# ══════════════════════════════════════════════════════════════════════════════

def restaurant_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Full per-restaurant aggregation."""
    delivered = df[df["order_status"] == "Delivered"]
    grp = df.groupby(["restaurant_id", "restaurant_name", "cuisine", "city"], observed=True).agg(
        total_orders=("order_id", "count"),
        delivered_orders=("order_status", lambda s: (s == "Delivered").sum()),
        cancelled_orders=("order_status", lambda s: (s == "Cancelled").sum()),
        total_revenue=("final_amount", "sum"),
        avg_order_value=("final_amount", "mean"),
        avg_rating=("customer_rating", "mean"),
        avg_delivery_time=("delivery_time_minutes", "mean"),
        avg_delivery_delay=("delivery_delay", "mean"),
    ).reset_index()

    grp["cancellation_rate"] = grp["cancelled_orders"] / grp["total_orders"] * 100
    grp["on_time_pct"] = grp.apply(
        lambda r: _on_time_pct_for_restaurant(df, r["restaurant_id"]), axis=1
    )
    return grp.sort_values("total_revenue", ascending=False).reset_index(drop=True)


def _on_time_pct_for_restaurant(df: pd.DataFrame, rest_id: str) -> float:
    sub = df[(df["restaurant_id"] == rest_id) & (df["order_status"] == "Delivered")]
    if len(sub) == 0:
        return np.nan
    return float((sub["delivery_delay"] <= 0).sum() / len(sub) * 100)


def top_restaurants_revenue(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    grp = df[df["order_status"] == "Delivered"].groupby(
        ["restaurant_id", "restaurant_name", "cuisine"], observed=True
    ).agg(
        revenue=("final_amount", "sum"),
        orders=("order_id", "count"),
        avg_rating=("customer_rating", "mean"),
    ).reset_index()
    return grp.nlargest(n, "revenue").reset_index(drop=True)


def top_restaurants_orders(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    grp = df.groupby(["restaurant_id", "restaurant_name", "cuisine"], observed=True).agg(
        orders=("order_id", "count"),
        revenue=("final_amount", "sum"),
        avg_rating=("customer_rating", "mean"),
    ).reset_index()
    return grp.nlargest(n, "orders").reset_index(drop=True)


def top_restaurants_rating(df: pd.DataFrame, n: int = 10, min_orders: int = 50) -> pd.DataFrame:
    grp = df.groupby(["restaurant_id", "restaurant_name", "cuisine"], observed=True).agg(
        orders=("order_id", "count"),
        avg_rating=("customer_rating", "mean"),
        revenue=("final_amount", "sum"),
    ).reset_index()
    return (
        grp[grp["orders"] >= min_orders]
        .nlargest(n, "avg_rating")
        .reset_index(drop=True)
    )


def revenue_vs_rating_scatter(df: pd.DataFrame) -> pd.DataFrame:
    """Per-restaurant: revenue, avg_rating, order volume (for bubble chart)."""
    grp = df[df["order_status"] == "Delivered"].groupby(
        ["restaurant_id", "restaurant_name", "cuisine"], observed=True
    ).agg(
        revenue=("final_amount", "sum"),
        avg_rating=("customer_rating", "mean"),
        orders=("order_id", "count"),
        avg_delivery_time=("delivery_time_minutes", "mean"),
    ).reset_index()
    return grp.dropna(subset=["avg_rating"])


# ══════════════════════════════════════════════════════════════════════════════
# Delivery analysis
# ══════════════════════════════════════════════════════════════════════════════

def delivery_time_by_restaurant(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    grp = df[df["order_status"] == "Delivered"].groupby(
        ["restaurant_name"], observed=True
    ).agg(
        avg_delivery=("delivery_time_minutes", "mean"),
        median_delivery=("delivery_time_minutes", "median"),
        orders=("order_id", "count"),
    ).reset_index()
    return grp[grp["orders"] >= 30].sort_values("avg_delivery", ascending=False).head(n)


def delivery_time_by_city(df: pd.DataFrame) -> pd.DataFrame:
    grp = df[df["order_status"] == "Delivered"].groupby("city", observed=True).agg(
        avg_delivery=("delivery_time_minutes", "mean"),
        median_delivery=("delivery_time_minutes", "median"),
        on_time_pct=("delivery_delay", lambda s: (s <= 0).mean() * 100),
    ).reset_index()
    return grp.sort_values("avg_delivery")


def estimated_vs_actual(df: pd.DataFrame) -> pd.DataFrame:
    sub = df[df["order_status"] == "Delivered"][
        ["estimated_delivery_time", "actual_delivery_time", "delivery_delay",
         "restaurant_name", "city"]
    ].dropna()
    return sub


def on_time_vs_delayed(df: pd.DataFrame) -> pd.DataFrame:
    delivered = df[df["order_status"] == "Delivered"].copy()
    delivered["perf"] = np.where(delivered["delivery_delay"] <= 0, "On Time / Early", "Delayed")
    grp = delivered.groupby("perf").agg(count=("order_id", "count")).reset_index()
    grp["pct"] = grp["count"] / grp["count"].sum() * 100
    return grp


# ══════════════════════════════════════════════════════════════════════════════
# Ratings analysis
# ══════════════════════════════════════════════════════════════════════════════

def rating_distribution(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.dropna(subset=["customer_rating"]).groupby("customer_rating").agg(
        count=("order_id", "count"),
    ).reset_index()
    return grp


def rating_by_cuisine(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.dropna(subset=["customer_rating"]).groupby("cuisine", observed=True).agg(
        avg_rating=("customer_rating", "mean"),
        orders=("order_id", "count"),
    ).reset_index()
    return grp.sort_values("avg_rating", ascending=False)


def rating_vs_delivery_time(df: pd.DataFrame, bins: int = 10) -> pd.DataFrame:
    """Bin delivery times and compute mean rating per bin."""
    sub = df.dropna(subset=["customer_rating", "delivery_time_minutes"]).copy()
    sub["dt_bin"] = pd.cut(sub["delivery_time_minutes"], bins=bins)
    grp = sub.groupby("dt_bin", observed=True).agg(
        avg_rating=("customer_rating", "mean"),
        orders=("order_id", "count"),
    ).reset_index()
    grp["dt_bin_mid"] = grp["dt_bin"].apply(lambda x: x.mid)
    return grp.dropna()


def rating_vs_delay(df: pd.DataFrame) -> pd.DataFrame:
    """Bin delivery delay and compute mean rating."""
    sub = df.dropna(subset=["customer_rating", "delivery_delay"]).copy()
    sub["delay_bin"] = pd.cut(
        sub["delivery_delay"],
        bins=[-60, -10, 0, 10, 20, 30, 60],
        labels=["Early >10m", "Early 0-10m", "On-Time", "Late 1-10m", "Late 11-20m", "Late >30m"],
    )
    grp = sub.groupby("delay_bin", observed=True).agg(
        avg_rating=("customer_rating", "mean"),
        orders=("order_id", "count"),
    ).reset_index()
    return grp.dropna()


# ══════════════════════════════════════════════════════════════════════════════
# Revenue analysis
# ══════════════════════════════════════════════════════════════════════════════

def revenue_by_cuisine(df: pd.DataFrame) -> pd.DataFrame:
    delivered = df[df["order_status"] == "Delivered"]
    grp = delivered.groupby("cuisine", observed=True).agg(
        revenue=("final_amount", "sum"),
        orders=("order_id", "count"),
        avg_order_value=("final_amount", "mean"),
    ).reset_index()
    grp["revenue_share"] = grp["revenue"] / grp["revenue"].sum() * 100
    return grp.sort_values("revenue", ascending=False).reset_index(drop=True)


def revenue_by_city(df: pd.DataFrame) -> pd.DataFrame:
    delivered = df[df["order_status"] == "Delivered"]
    grp = delivered.groupby("city", observed=True).agg(
        revenue=("final_amount", "sum"),
        orders=("order_id", "count"),
    ).reset_index()
    grp["revenue_share"] = grp["revenue"] / grp["revenue"].sum() * 100
    return grp.sort_values("revenue", ascending=False).reset_index(drop=True)


def avg_order_value_trend(df: pd.DataFrame) -> pd.DataFrame:
    delivered = df[df["order_status"] == "Delivered"]
    grp = delivered.groupby("month_name", observed=True).agg(
        avg_order_value=("final_amount", "mean"),
        orders=("order_id", "count"),
    ).reset_index()
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    grp["month_name"] = pd.Categorical(grp["month_name"], categories=month_order, ordered=True)
    return grp.sort_values("month_name").reset_index(drop=True)


# ══════════════════════════════════════════════════════════════════════════════
# Advanced analytics
# ══════════════════════════════════════════════════════════════════════════════

def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pearson correlation among key numeric metrics.
    """
    cols = [
        "order_amount", "final_amount", "delivery_time_minutes",
        "delivery_delay", "customer_rating", "distance_km",
        "number_of_items", "discount",
    ]
    sub = df[[c for c in cols if c in df.columns]].copy()
    return sub.corr(numeric_only=True)


def restaurant_performance_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transparent composite restaurant score.

    Score = 0.30 × revenue_norm
           + 0.25 × order_volume_norm
           + 0.25 × rating_norm
           + 0.20 × on_time_pct_norm

    All components normalized to [0, 1].
    """
    summary = restaurant_summary(df)

    # Only restaurants with meaningful data
    summary = summary[summary["delivered_orders"] >= 20].copy()

    summary["revenue_norm"]    = normalize_series(summary["total_revenue"])
    summary["vol_norm"]        = normalize_series(summary["delivered_orders"].astype(float))
    summary["rating_norm"]     = normalize_series(summary["avg_rating"].fillna(summary["avg_rating"].median()))
    summary["on_time_norm"]    = normalize_series(summary["on_time_pct"].fillna(0))

    summary["performance_score"] = (
        0.30 * summary["revenue_norm"]
        + 0.25 * summary["vol_norm"]
        + 0.25 * summary["rating_norm"]
        + 0.20 * summary["on_time_norm"]
    )

    cols = [
        "restaurant_name", "cuisine", "city",
        "delivered_orders", "total_revenue", "avg_rating",
        "avg_delivery_time", "on_time_pct", "performance_score",
    ]
    return (
        summary[cols]
        .sort_values("performance_score", ascending=False)
        .reset_index(drop=True)
    )


def peak_period_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Order volume and revenue by day-of-week × time-of-day."""
    grp = df.groupby(["day_name", "time_of_day"], observed=True).agg(
        orders=("order_id", "count"),
        revenue=("final_amount", "sum"),
    ).reset_index()
    return grp
