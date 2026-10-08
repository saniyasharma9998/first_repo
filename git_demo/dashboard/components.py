"""
dashboard/components.py
-----------------------
Reusable Plotly chart builders and Streamlit UI helpers for the dashboard.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.utils import CHART_COLORS, PALETTE, fmt_inr, fmt_mins, fmt_number, fmt_pct

# ── Chart defaults ─────────────────────────────────────────────────────────────

_FONT   = dict(family="'Segoe UI', system-ui, sans-serif", size=12, color="#1f2328")
_MARGIN = dict(l=40, r=20, t=50, b=40)


def _base_layout(**kwargs) -> dict:
    return dict(
        font=_FONT,
        margin=_MARGIN,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        **kwargs,
    )


# ══════════════════════════════════════════════════════════════════════════════
# KPI cards (rendered as Streamlit markdown / st.metric)
# ══════════════════════════════════════════════════════════════════════════════

def kpi_card_html(
    label: str,
    value: str,
    delta: str | None = None,
    delta_positive: bool | None = None,
    icon: str = "📊",
) -> str:
    """Return HTML for a styled KPI card."""
    delta_color = "#16a34a" if delta_positive else "#dc2626"
    delta_html = (
        f'<p style="color:{delta_color};font-size:0.78rem;margin:0">{delta}</p>'
        if delta
        else ""
    )
    return f"""
    <div style="
        background:#ffffff;
        border:1px solid #e5e7eb;
        border-radius:10px;
        padding:16px 20px;
        min-height:100px;
        box-shadow:0 1px 3px rgba(0,0,0,.06)
    ">
      <p style="color:#57606a;font-size:0.78rem;margin:0 0 4px 0;text-transform:uppercase;letter-spacing:.05em">{icon} {label}</p>
      <p style="color:#1a3a5c;font-size:1.6rem;font-weight:700;margin:0">{value}</p>
      {delta_html}
    </div>
    """


# ══════════════════════════════════════════════════════════════════════════════
# Line charts
# ══════════════════════════════════════════════════════════════════════════════

def chart_orders_over_time(df_time: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=df_time["date"], y=df_time["orders"],
            name="Orders", line=dict(color=PALETTE["primary"], width=2),
            fill="tozeroy", fillcolor="rgba(26,58,92,0.08)",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df_time["date"], y=df_time["revenue"],
            name="Revenue (₹)", line=dict(color=PALETTE["secondary"], width=2, dash="dot"),
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title="Weekly Order Volume & Revenue Trend",
        **_base_layout(),
    )
    fig.update_yaxes(title_text="Orders", secondary_y=False, showgrid=True, gridcolor="#f0f0f0")
    fig.update_yaxes(title_text="Revenue (₹)", secondary_y=True, showgrid=False)
    fig.update_xaxes(showgrid=False)
    return fig


def chart_revenue_trend(df_time: pd.DataFrame) -> go.Figure:
    fig = px.area(
        df_time, x="date", y="revenue",
        labels={"date": "Date", "revenue": "Revenue (₹)"},
        title="Revenue Trend Over Time",
        color_discrete_sequence=[PALETTE["secondary"]],
    )
    fig.update_traces(line_color=PALETTE["secondary"], fillcolor="rgba(13,148,136,0.15)")
    fig.update_layout(**_base_layout())
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Bar charts
# ══════════════════════════════════════════════════════════════════════════════

def chart_orders_by_month(df_month: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df_month, x="month_name", y="orders",
        title="Monthly Order Volume — Weekends Drive Peak Months",
        labels={"month_name": "Month", "orders": "Orders"},
        color="orders",
        color_continuous_scale=[[0, "#c7d9f0"], [1, PALETTE["primary"]]],
    )
    fig.update_layout(**_base_layout(), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def chart_orders_by_day(df_day: pd.DataFrame) -> go.Figure:
    colors = [PALETTE["accent"] if d in ["Saturday", "Sunday"] else PALETTE["primary"]
              for d in df_day["day_name"]]
    fig = go.Figure(go.Bar(
        x=df_day["day_name"], y=df_day["orders"],
        marker_color=colors, name="Orders",
    ))
    fig.update_layout(
        title="Orders by Day of Week — Weekends Are 30%+ Busier",
        xaxis_title="Day", yaxis_title="Orders",
        **_base_layout(),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def chart_orders_by_hour(df_hour: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df_hour, x="order_hour", y="orders",
        title="Hourly Order Distribution — Lunch & Dinner Peaks",
        labels={"order_hour": "Hour of Day", "orders": "Orders"},
        color="orders",
        color_continuous_scale=[[0, "#fde8d0"], [1, PALETTE["accent"]]],
    )
    fig.add_vline(x=12, line_dash="dash", line_color=PALETTE["secondary"],
                  annotation_text="Lunch Peak", annotation_position="top right")
    fig.add_vline(x=19, line_dash="dash", line_color=PALETTE["primary"],
                  annotation_text="Dinner Peak", annotation_position="top right")
    fig.update_layout(**_base_layout(), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=False, dtick=2)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def chart_orders_by_cuisine(df_cuisine: pd.DataFrame) -> go.Figure:
    top = df_cuisine.head(10)
    fig = px.bar(
        top.sort_values("orders"), x="orders", y="cuisine",
        orientation="h",
        title="Orders by Cuisine — North Indian & Chinese Lead",
        labels={"orders": "Orders", "cuisine": "Cuisine"},
        color="orders",
        color_continuous_scale=[[0, "#cce5ff"], [1, PALETTE["primary"]]],
    )
    fig.update_layout(**_base_layout(), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    fig.update_yaxes(showgrid=False)
    return fig


def chart_revenue_by_city(df_city: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df_city, x="city", y="revenue",
        title="Revenue by City — Mumbai & Delhi Are Top Markets",
        labels={"city": "City", "revenue": "Revenue (₹)"},
        color="revenue",
        color_continuous_scale=[[0, "#ccfbf1"], [1, PALETTE["secondary"]]],
    )
    fig.update_layout(**_base_layout(), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def chart_order_status(df_status: pd.DataFrame) -> go.Figure:
    color_map = {
        "Delivered": PALETTE["positive"],
        "Cancelled": PALETTE["negative"],
        "Pending":   PALETTE["accent"],
    }
    colors = [color_map.get(s, PALETTE["neutral"]) for s in df_status["order_status"]]
    fig = go.Figure(go.Pie(
        labels=df_status["order_status"],
        values=df_status["count"],
        marker=dict(colors=colors),
        hole=0.5,
        textinfo="label+percent",
    ))
    fig.update_layout(
        title="Order Status Distribution",
        **_base_layout(),
    )
    return fig


# ── Restaurant section ─────────────────────────────────────────────────────────

def chart_top_restaurants_revenue(df_top: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df_top.sort_values("revenue"), x="revenue", y="restaurant_name",
        orientation="h",
        title="Top 10 Restaurants by Revenue",
        labels={"revenue": "Revenue (₹)", "restaurant_name": "Restaurant"},
        color="revenue",
        color_continuous_scale=[[0, "#c7d9f0"], [1, PALETTE["primary"]]],
        hover_data={"avg_rating": ":.2f", "orders": True},
    )
    fig.update_layout(**_base_layout(), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def chart_top_restaurants_orders(df_top: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df_top.sort_values("orders"), x="orders", y="restaurant_name",
        orientation="h",
        title="Top 10 Restaurants by Order Volume",
        labels={"orders": "Orders", "restaurant_name": "Restaurant"},
        color="orders",
        color_continuous_scale=[[0, "#ccfbf1"], [1, PALETTE["secondary"]]],
        hover_data={"avg_rating": ":.2f", "revenue": True},
    )
    fig.update_layout(**_base_layout(), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def chart_revenue_vs_rating(df_scatter: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df_scatter, x="avg_rating", y="revenue",
        size="orders", color="cuisine",
        hover_name="restaurant_name",
        title="Revenue vs Customer Rating (bubble = order volume)",
        labels={"avg_rating": "Average Rating", "revenue": "Revenue (₹)", "cuisine": "Cuisine"},
        color_discrete_sequence=CHART_COLORS,
        size_max=40,
    )
    fig.update_layout(**_base_layout())
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0", range=[1, 5.5])
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


# ── Delivery section ───────────────────────────────────────────────────────────

def chart_delivery_time_dist(df: pd.DataFrame) -> go.Figure:
    delivered = df[df["order_status"] == "Delivered"]["delivery_time_minutes"].dropna()
    fig = px.histogram(
        delivered, nbins=30,
        title="Delivery Time Distribution — Most Orders Arrive in 25–50 Minutes",
        labels={"value": "Delivery Time (min)", "count": "Orders"},
        color_discrete_sequence=[PALETTE["primary"]],
    )
    fig.add_vline(
        x=delivered.median(), line_dash="dash", line_color=PALETTE["accent"],
        annotation_text=f"Median: {delivered.median():.0f} min",
        annotation_position="top right",
    )
    fig.update_layout(**_base_layout())
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def chart_delivery_time_by_restaurant(df_rest: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df_rest.sort_values("avg_delivery", ascending=True),
        x="avg_delivery", y="restaurant_name",
        orientation="h",
        title="Restaurants with Slowest Average Delivery Times",
        labels={"avg_delivery": "Avg Delivery Time (min)", "restaurant_name": "Restaurant"},
        color="avg_delivery",
        color_continuous_scale=[[0, "#fef9c3"], [1, "#dc2626"]],
    )
    fig.update_layout(**_base_layout(), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def chart_estimated_vs_actual(df_evsa: pd.DataFrame) -> go.Figure:
    sample = df_evsa.sample(min(1500, len(df_evsa)), random_state=42)
    fig = px.scatter(
        sample, x="estimated_delivery_time", y="actual_delivery_time",
        opacity=0.4,
        title="Estimated vs Actual Delivery Time — Platform Often Under-Estimates",
        labels={
            "estimated_delivery_time": "Estimated Time (min)",
            "actual_delivery_time": "Actual Time (min)",
        },
        color_discrete_sequence=[PALETTE["primary"]],
    )
    max_val = max(sample["estimated_delivery_time"].max(), sample["actual_delivery_time"].max())
    fig.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val],
        mode="lines", line=dict(color=PALETTE["accent"], dash="dash"),
        name="Perfect Estimate",
    ))
    fig.update_layout(**_base_layout())
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def chart_on_time_vs_delayed(df_otd: pd.DataFrame) -> go.Figure:
    color_map = {
        "On Time / Early": PALETTE["positive"],
        "Delayed":         PALETTE["negative"],
    }
    colors = [color_map.get(p, PALETTE["neutral"]) for p in df_otd["perf"]]
    fig = go.Figure(go.Pie(
        labels=df_otd["perf"], values=df_otd["count"],
        marker=dict(colors=colors), hole=0.5,
        textinfo="label+percent",
    ))
    fig.update_layout(title="On-Time vs Delayed Deliveries", **_base_layout())
    return fig


def chart_delivery_by_city(df_city: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df_city, x="city", y="avg_delivery",
        error_y=None,
        title="Average Delivery Time by City",
        labels={"city": "City", "avg_delivery": "Avg Delivery Time (min)"},
        color="avg_delivery",
        color_continuous_scale=[[0, "#ccfbf1"], [1, PALETTE["primary"]]],
    )
    fig.update_layout(**_base_layout(), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


# ── Rating section ─────────────────────────────────────────────────────────────

def chart_rating_distribution(df_ratings: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df_ratings, x="customer_rating", y="count",
        title="Customer Rating Distribution — Majority Rate 3.5–5",
        labels={"customer_rating": "Rating", "count": "Orders"},
        color="customer_rating",
        color_continuous_scale=[[0, "#fef2f2"], [0.5, "#fef9c3"], [1, "#f0fdf4"]],
    )
    fig.update_layout(**_base_layout(), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def chart_rating_by_cuisine(df_cuisine: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df_cuisine, x="avg_rating", y="cuisine",
        orientation="h",
        title="Average Rating by Cuisine",
        labels={"avg_rating": "Average Rating", "cuisine": "Cuisine"},
        color="avg_rating",
        color_continuous_scale=[[0, "#fef2f2"], [0.5, "#fef9c3"], [1, "#f0fdf4"]],
    )
    fig.update_layout(**_base_layout(), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0", range=[0, 5])
    return fig


def chart_rating_vs_delivery(df_rtd: pd.DataFrame) -> go.Figure:
    fig = px.line(
        df_rtd, x="dt_bin_mid", y="avg_rating",
        title="Longer Delivery Times Correlate with Lower Ratings",
        labels={"dt_bin_mid": "Delivery Time (min)", "avg_rating": "Average Rating"},
        markers=True,
        color_discrete_sequence=[PALETTE["primary"]],
    )
    fig.update_layout(**_base_layout())
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0", range=[1, 5])
    return fig


def chart_rating_vs_delay(df_rtvd: pd.DataFrame) -> go.Figure:
    bar_colors = [
        PALETTE["positive"] if "Early" in str(d) or d == "On-Time" else PALETTE["negative"]
        for d in df_rtvd["delay_bin"]
    ]
    fig = go.Figure(go.Bar(
        x=df_rtvd["delay_bin"].astype(str),
        y=df_rtvd["avg_rating"],
        marker_color=bar_colors,
        text=df_rtvd["avg_rating"].round(2),
        textposition="outside",
    ))
    fig.update_layout(
        title="Early/On-Time Deliveries Earn Significantly Higher Ratings",
        xaxis_title="Delivery Delay Category",
        yaxis_title="Average Rating",
        **_base_layout(),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0", range=[0, 5.5])
    return fig


# ── Revenue section ────────────────────────────────────────────────────────────

def chart_revenue_by_cuisine(df_rev_cuisine: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df_rev_cuisine.sort_values("revenue", ascending=True).head(12),
        x="revenue", y="cuisine",
        orientation="h",
        title="Revenue by Cuisine — North Indian Dominates",
        labels={"revenue": "Revenue (₹)", "cuisine": "Cuisine"},
        color="revenue",
        color_continuous_scale=[[0, "#cce5ff"], [1, PALETTE["primary"]]],
    )
    fig.update_layout(**_base_layout(), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def chart_avg_order_value_trend(df_aov: pd.DataFrame) -> go.Figure:
    fig = px.line(
        df_aov, x="month_name", y="avg_order_value",
        title="Average Order Value Trend by Month",
        labels={"month_name": "Month", "avg_order_value": "Avg Order Value (₹)"},
        markers=True,
        color_discrete_sequence=[PALETTE["accent"]],
    )
    fig.update_layout(**_base_layout())
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    return fig


def chart_revenue_contribution(df_top: pd.DataFrame) -> go.Figure:
    """Donut of revenue contribution by top restaurants vs others."""
    total = df_top["revenue"].sum()
    top10 = df_top.head(10)
    other_rev = total - top10["revenue"].sum()
    labels = list(top10["restaurant_name"]) + ["Others"]
    values = list(top10["revenue"]) + [max(0, other_rev)]
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.45, textinfo="percent",
    ))
    fig.update_layout(
        title="Revenue Concentration — Top 10 Restaurants",
        **_base_layout(),
    )
    return fig


# ── Correlation heatmap ────────────────────────────────────────────────────────

def chart_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    labels = [
        c.replace("_", " ").title()
        for c in corr_df.columns
    ]
    fig = go.Figure(go.Heatmap(
        z=corr_df.values,
        x=labels,
        y=labels,
        colorscale="RdBu",
        zmid=0,
        text=corr_df.round(2).values,
        texttemplate="%{text}",
    ))
    fig.update_layout(
        title="Correlation Matrix — Delivery Time Negatively Impacts Ratings",
        **_base_layout(),
    )
    return fig


# ── Performance score bar ──────────────────────────────────────────────────────

def chart_performance_score(df_score: pd.DataFrame) -> go.Figure:
    top = df_score.head(15)
    fig = px.bar(
        top.sort_values("performance_score"),
        x="performance_score", y="restaurant_name",
        orientation="h",
        title="Restaurant Performance Score (Top 15) — Balanced Across Revenue, Rating & Speed",
        labels={"performance_score": "Score (0–1)", "restaurant_name": "Restaurant"},
        color="performance_score",
        color_continuous_scale=[[0, "#f0fdf4"], [1, PALETTE["secondary"]]],
        hover_data={"avg_rating": ":.2f", "total_revenue": True, "on_time_pct": ":.1f"},
    )
    fig.update_layout(**_base_layout(), coloraxis_showscale=False)
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0", range=[0, 1.05])
    return fig
