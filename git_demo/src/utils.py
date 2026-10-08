"""
utils.py
--------
Shared utility helpers used across the project.
"""

from pathlib import Path
import pandas as pd
import numpy as np


# ── Path helpers ───────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(__file__).resolve().parent.parent
RAW_DATA      = PROJECT_ROOT / "data" / "raw"  / "food_delivery_orders.csv"
PROCESSED_DATA = PROJECT_ROOT / "data" / "processed" / "cleaned_food_delivery_orders.csv"


def load_processed(path: str | Path = PROCESSED_DATA) -> pd.DataFrame:
    """Load the cleaned dataset; raise a helpful error if not found."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Processed data not found at {path}.\n"
            "Run:  python src/data_generation.py && python src/data_cleaning.py"
        )
    df = pd.read_csv(path, low_memory=False, parse_dates=["order_date"])
    return df


# ── Number formatting ──────────────────────────────────────────────────────────

def fmt_inr(value: float, decimals: int = 1) -> str:
    """Format a number as Indian Rupees (₹12.4M, ₹345K, ₹1,200)."""
    if pd.isna(value):
        return "N/A"
    if abs(value) >= 1_000_000:
        return f"₹{value/1_000_000:.{decimals}f}M"
    if abs(value) >= 1_000:
        return f"₹{value/1_000:.{decimals}f}K"
    return f"₹{value:,.0f}"


def fmt_number(value: float, decimals: int = 1) -> str:
    """Format large numbers with K/M suffixes."""
    if pd.isna(value):
        return "N/A"
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.{decimals}f}M"
    if abs(value) >= 1_000:
        return f"{value/1_000:.{decimals}f}K"
    return f"{value:,.{decimals}f}"


def fmt_pct(value: float, decimals: int = 1) -> str:
    """Format as percentage string."""
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}%"


def fmt_mins(value: float) -> str:
    """Format minutes as '32 min'."""
    if pd.isna(value):
        return "N/A"
    return f"{value:.1f} min"


# ── Statistical helpers ────────────────────────────────────────────────────────

def normalize_series(s: pd.Series) -> pd.Series:
    """Min-max normalize a series to [0, 1]."""
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - mn) / (mx - mn)


def iqr_bounds(series: pd.Series, factor: float = 1.5) -> tuple[float, float]:
    """Return (lower, upper) IQR-based outlier fences."""
    q1  = series.quantile(0.25)
    q3  = series.quantile(0.75)
    iqr = q3 - q1
    return q1 - factor * iqr, q3 + factor * iqr


# ── Color palette (Plotly-compatible) ─────────────────────────────────────────

PALETTE = {
    "primary":   "#1a3a5c",   # dark navy blue
    "secondary": "#0d9488",   # teal
    "accent":    "#f97316",   # orange
    "positive":  "#16a34a",   # green
    "negative":  "#dc2626",   # red
    "neutral":   "#64748b",   # slate gray
    "bg":        "#f8fafc",   # light background
    "surface":   "#ffffff",
}

CHART_COLORS = [
    "#1a3a5c", "#0d9488", "#f97316", "#7c3aed",
    "#db2777", "#16a34a", "#ca8a04", "#0284c7",
    "#9333ea", "#dc2626", "#059669", "#d97706",
]


# ── Month ordering ─────────────────────────────────────────────────────────────

MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

DAY_ORDER   = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
