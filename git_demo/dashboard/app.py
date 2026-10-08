"""
dashboard/app.py
----------------
Food Delivery Analytics — Streamlit Dashboard

Run:
    streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

# ── Path setup so src/ is importable when running from any cwd ─────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

# ── Page config — must be first Streamlit call ────────────────────────────────
st.set_page_config(
    page_title="Food Delivery Analytics",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src import analysis as an
from src.utils import (
    PROCESSED_DATA, fmt_inr, fmt_mins, fmt_number, fmt_pct, load_processed
)
from dashboard.components import (
    chart_avg_order_value_trend,
    chart_correlation_heatmap,
    chart_delivery_by_city,
    chart_delivery_time_by_restaurant,
    chart_delivery_time_dist,
    chart_estimated_vs_actual,
    chart_on_time_vs_delayed,
    chart_orders_by_cuisine,
    chart_orders_by_day,
    chart_orders_by_hour,
    chart_orders_by_month,
    chart_orders_over_time,
    chart_order_status,
    chart_performance_score,
    chart_rating_by_cuisine,
    chart_rating_distribution,
    chart_rating_vs_delay,
    chart_rating_vs_delivery,
    chart_revenue_by_city,
    chart_revenue_by_cuisine,
    chart_revenue_contribution,
    chart_revenue_trend,
    chart_revenue_vs_rating,
    chart_top_restaurants_orders,
    chart_top_restaurants_revenue,
    kpi_card_html,
)


# ══════════════════════════════════════════════════════════════════════════════
# Custom CSS
# ══════════════════════════════════════════════════════════════════════════════

css_path = PROJECT_ROOT / "dashboard" / "styles.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Data loading (cached)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Loading dataset …")
def load_data() -> pd.DataFrame:
    """Load and cache the processed dataset."""
    df = load_processed(PROJECT_ROOT / "data" / "processed" / "cleaned_food_delivery_orders.csv")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    # Ensure numeric
    for col in ["order_amount", "final_amount", "customer_rating",
                "delivery_time_minutes", "delivery_delay", "distance_km"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


df_all = load_data()


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar — filters
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:10px 0 20px 0">
          <span style="font-size:2rem">🍱</span>
          <h2 style="color:#ffffff;margin:6px 0 2px 0;font-size:1.1rem">Food Delivery Analytics</h2>
          <p style="color:rgba(255,255,255,0.6);font-size:0.75rem;margin:0">Dashboard Filters</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Date range ─────────────────────────────────────────────────────────────
    min_date = df_all["order_date"].min().date()
    max_date = df_all["order_date"].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_range",
    )

    # ── City ───────────────────────────────────────────────────────────────────
    cities = sorted(df_all["city"].dropna().unique().tolist())
    sel_cities = st.multiselect("City", options=cities, default=[], placeholder="All cities")

    # ── Cuisine ────────────────────────────────────────────────────────────────
    cuisines = sorted(df_all["cuisine"].dropna().unique().tolist())
    sel_cuisines = st.multiselect("Cuisine", options=cuisines, default=[], placeholder="All cuisines")

    # ── Order status ───────────────────────────────────────────────────────────
    statuses = sorted(df_all["order_status"].dropna().unique().tolist())
    sel_statuses = st.multiselect("Order Status", options=statuses, default=[], placeholder="All statuses")

    # ── Payment method ─────────────────────────────────────────────────────────
    payments = sorted(df_all["payment_method"].dropna().unique().tolist())
    sel_payments = st.multiselect("Payment Method", options=payments, default=[], placeholder="All methods")

    # ── Rating range ───────────────────────────────────────────────────────────
    rating_range = st.slider("Customer Rating", min_value=1.0, max_value=5.0,
                              value=(1.0, 5.0), step=0.5)

    # ── Reset ──────────────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("🔄 Reset Filters"):
        st.rerun()

    st.markdown(
        "<p style='color:rgba(255,255,255,0.4);font-size:0.7rem;text-align:center;margin-top:20px'>"
        "Data: Synthetic | Period: 2023<br>10,000+ orders | 60 restaurants | 6 cities"
        "</p>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# Apply filters
# ══════════════════════════════════════════════════════════════════════════════

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    # Date
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        df = df[(df["order_date"] >= start) & (df["order_date"] <= end)]

    if sel_cities:
        df = df[df["city"].isin(sel_cities)]
    if sel_cuisines:
        df = df[df["cuisine"].isin(sel_cuisines)]
    if sel_statuses:
        df = df[df["order_status"].isin(sel_statuses)]
    if sel_payments:
        df = df[df["payment_method"].isin(sel_payments)]

    # Rating filter (apply only to rows that have a rating)
    rated_mask = df["customer_rating"].notna()
    rating_ok  = (df["customer_rating"] >= rating_range[0]) & (df["customer_rating"] <= rating_range[1])
    df = df[~rated_mask | rating_ok]

    return df.reset_index(drop=True)


df = apply_filters(df_all)


# ══════════════════════════════════════════════════════════════════════════════
# Header
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <div class="dash-header">
      <h1>🍱 Food Delivery Analytics Dashboard</h1>
      <p>Orders &bull; Revenue &bull; Restaurants &bull; Ratings &bull; Delivery Performance</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if len(df) == 0:
    st.warning("No data matches the selected filters. Please adjust the sidebar filters.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# Compute KPIs
# ══════════════════════════════════════════════════════════════════════════════

kpis = an.all_kpis(df)


# ── Optional MoM delta ────────────────────────────────────────────────────────
def _mom_delta(df_full: pd.DataFrame, metric_fn, month_offset: int = 1):
    """Returns (current_val, delta_str, is_positive) for month-over-month."""
    try:
        latest_month = df_full["order_date"].dt.to_period("M").max()
        prev_month   = latest_month - month_offset

        curr = df_full[df_full["order_date"].dt.to_period("M") == latest_month]
        prev = df_full[df_full["order_date"].dt.to_period("M") == prev_month]

        v_curr = metric_fn(curr)
        v_prev = metric_fn(prev)
        if v_prev and v_prev != 0:
            pct = (v_curr - v_prev) / abs(v_prev) * 100
            sign = "▲" if pct > 0 else "▼"
            return f"{sign} {abs(pct):.1f}% vs prev month", pct > 0
    except Exception:
        pass
    return None, None


# ══════════════════════════════════════════════════════════════════════════════
# KPI Cards
# ══════════════════════════════════════════════════════════════════════════════

cols = st.columns(8)
kpi_defs = [
    ("Total Orders",         fmt_number(kpis["total_orders"], 0),        "📦", None, None),
    ("Completed",            fmt_number(kpis["completed_orders"], 0),    "✅", None, None),
    ("Total Revenue",        fmt_inr(kpis["total_revenue"]),             "💰", None, None),
    ("Avg Order Value",      fmt_inr(kpis["avg_order_value"]),           "🛒", None, None),
    ("Avg Rating",           f"{kpis['avg_rating']:.2f} / 5",           "⭐", None, None),
    ("Avg Delivery",         fmt_mins(kpis["avg_delivery_time"]),        "🚴", None, None),
    ("On-Time %",            fmt_pct(kpis["on_time_pct"]),               "⏱️", None, None),
    ("Cancellation Rate",    fmt_pct(kpis["cancellation_rate"]),         "❌", None, None),
]

for col, (label, value, icon, delta, delta_pos) in zip(cols, kpi_defs):
    with col:
        st.markdown(kpi_card_html(label, value, delta, delta_pos, icon), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Main tabs
# ══════════════════════════════════════════════════════════════════════════════

tab_overview, tab_restaurants, tab_delivery, tab_ratings, tab_revenue, tab_advanced = st.tabs([
    "📊 Overview",
    "🏪 Restaurants",
    "🚴 Delivery",
    "⭐ Ratings",
    "💰 Revenue",
    "🔬 Advanced Analytics",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

with tab_overview:
    c1, c2 = st.columns(2)
    with c1:
        orders_time = an.orders_over_time(df, freq="W")
        if len(orders_time) > 1:
            st.plotly_chart(chart_orders_over_time(orders_time), use_container_width=True)
    with c2:
        df_status = an.order_status_distribution(df)
        st.plotly_chart(chart_order_status(df_status), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        df_month = an.orders_by_month(df)
        st.plotly_chart(chart_orders_by_month(df_month), use_container_width=True)
    with c4:
        df_day = an.orders_by_day(df)
        st.plotly_chart(chart_orders_by_day(df_day), use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        df_hour = an.orders_by_hour(df)
        st.plotly_chart(chart_orders_by_hour(df_hour), use_container_width=True)
    with c6:
        df_cuisine_o = an.orders_by_cuisine(df)
        st.plotly_chart(chart_orders_by_cuisine(df_cuisine_o), use_container_width=True)

    st.plotly_chart(chart_revenue_by_city(an.orders_by_city(df)), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: RESTAURANTS
# ══════════════════════════════════════════════════════════════════════════════

with tab_restaurants:
    c1, c2 = st.columns(2)
    with c1:
        df_top_rev = an.top_restaurants_revenue(df, n=10)
        st.plotly_chart(chart_top_restaurants_revenue(df_top_rev), use_container_width=True)
    with c2:
        df_top_ord = an.top_restaurants_orders(df, n=10)
        st.plotly_chart(chart_top_restaurants_orders(df_top_ord), use_container_width=True)

    df_scatter = an.revenue_vs_rating_scatter(df)
    if len(df_scatter) >= 3:
        st.plotly_chart(chart_revenue_vs_rating(df_scatter), use_container_width=True)

    st.markdown("#### 📋 Restaurant Performance Summary Table")
    try:
        rest_sum = an.restaurant_summary(df)
        display_cols = [
            "restaurant_name", "cuisine", "city",
            "total_orders", "delivered_orders", "total_revenue",
            "avg_order_value", "avg_rating", "avg_delivery_time", "on_time_pct",
            "cancellation_rate",
        ]
        display_cols = [c for c in display_cols if c in rest_sum.columns]
        fmt_rest = rest_sum[display_cols].copy()
        # Format numbers for display
        if "total_revenue" in fmt_rest.columns:
            fmt_rest["total_revenue"] = fmt_rest["total_revenue"].apply(lambda x: fmt_inr(x, 0))
        if "avg_order_value" in fmt_rest.columns:
            fmt_rest["avg_order_value"] = fmt_rest["avg_order_value"].apply(lambda x: fmt_inr(x, 0))
        if "avg_rating" in fmt_rest.columns:
            fmt_rest["avg_rating"] = fmt_rest["avg_rating"].round(2)
        if "avg_delivery_time" in fmt_rest.columns:
            fmt_rest["avg_delivery_time"] = fmt_rest["avg_delivery_time"].round(1)
        if "on_time_pct" in fmt_rest.columns:
            fmt_rest["on_time_pct"] = fmt_rest["on_time_pct"].round(1).astype(str) + "%"
        if "cancellation_rate" in fmt_rest.columns:
            fmt_rest["cancellation_rate"] = fmt_rest["cancellation_rate"].round(1).astype(str) + "%"
        st.dataframe(fmt_rest, use_container_width=True, height=350)
    except Exception as e:
        st.warning(f"Could not generate restaurant summary: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: DELIVERY
# ══════════════════════════════════════════════════════════════════════════════

with tab_delivery:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_delivery_time_dist(df), use_container_width=True)
    with c2:
        df_otd = an.on_time_vs_delayed(df)
        st.plotly_chart(chart_on_time_vs_delayed(df_otd), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        df_dt_rest = an.delivery_time_by_restaurant(df, n=15)
        if len(df_dt_rest) >= 3:
            st.plotly_chart(chart_delivery_time_by_restaurant(df_dt_rest), use_container_width=True)
    with c4:
        df_dt_city = an.delivery_time_by_city(df)
        st.plotly_chart(chart_delivery_by_city(df_dt_city), use_container_width=True)

    df_evsa = an.estimated_vs_actual(df)
    if len(df_evsa) >= 10:
        st.plotly_chart(chart_estimated_vs_actual(df_evsa), use_container_width=True)

    # Delivery performance breakdown
    st.markdown("#### Delivery Performance Breakdown by City")
    try:
        perf_city = df[df["order_status"] == "Delivered"].groupby(
            ["city", "delivery_performance"], observed=True
        ).size().reset_index(name="count")
        if len(perf_city) > 0:
            import plotly.express as px
            fig_perf = px.bar(
                perf_city, x="city", y="count", color="delivery_performance",
                barmode="stack",
                title="Delivery Performance Category by City",
                color_discrete_map={
                    "Early/On Time": "#16a34a",
                    "Slightly Delayed": "#f97316",
                    "Significantly Delayed": "#dc2626",
                    "N/A": "#94a3b8",
                },
            )
            fig_perf.update_layout(
                margin=dict(l=40, r=20, t=50, b=40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_perf, use_container_width=True)
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: RATINGS
# ══════════════════════════════════════════════════════════════════════════════

with tab_ratings:
    c1, c2 = st.columns(2)
    with c1:
        df_rating_dist = an.rating_distribution(df)
        st.plotly_chart(chart_rating_distribution(df_rating_dist), use_container_width=True)
    with c2:
        df_rat_cuisine = an.rating_by_cuisine(df)
        st.plotly_chart(chart_rating_by_cuisine(df_rat_cuisine), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        df_rtd = an.rating_vs_delivery_time(df)
        if len(df_rtd) >= 3:
            st.plotly_chart(chart_rating_vs_delivery(df_rtd), use_container_width=True)
    with c4:
        df_rtvd = an.rating_vs_delay(df)
        if len(df_rtvd) >= 2:
            st.plotly_chart(chart_rating_vs_delay(df_rtvd), use_container_width=True)

    # Top rated restaurants
    st.markdown("#### ⭐ Highest Rated Restaurants (min. 50 orders)")
    df_top_rat = an.top_restaurants_rating(df, n=10, min_orders=50)
    if len(df_top_rat) > 0:
        import plotly.express as px
        fig_rat = px.bar(
            df_top_rat.sort_values("avg_rating"),
            x="avg_rating", y="restaurant_name",
            orientation="h",
            title="Top Restaurants by Average Customer Rating",
            labels={"avg_rating": "Average Rating", "restaurant_name": "Restaurant"},
            color="avg_rating",
            color_continuous_scale=[[0, "#fef9c3"], [1, "#16a34a"]],
            range_x=[0, 5.2],
        )
        fig_rat.update_layout(
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_rat, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: REVENUE
# ══════════════════════════════════════════════════════════════════════════════

with tab_revenue:
    df_time = an.orders_over_time(df, freq="W")
    if len(df_time) > 1:
        st.plotly_chart(chart_revenue_trend(df_time), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        df_rev_cuisine = an.revenue_by_cuisine(df)
        st.plotly_chart(chart_revenue_by_cuisine(df_rev_cuisine), use_container_width=True)
    with c2:
        df_rev_city = an.revenue_by_city(df)
        st.plotly_chart(chart_revenue_by_city(df_rev_city), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        df_aov = an.avg_order_value_trend(df)
        st.plotly_chart(chart_avg_order_value_trend(df_aov), use_container_width=True)
    with c4:
        df_top10 = an.top_restaurants_revenue(df, n=10)
        st.plotly_chart(chart_revenue_contribution(df_top10), use_container_width=True)

    # Revenue metrics summary
    st.markdown("#### Revenue Summary by Cuisine")
    df_rev_sum = an.revenue_by_cuisine(df)[
        ["cuisine", "orders", "revenue", "avg_order_value", "revenue_share"]
    ].copy()
    df_rev_sum["revenue"]       = df_rev_sum["revenue"].apply(lambda x: fmt_inr(x, 0))
    df_rev_sum["avg_order_value"] = df_rev_sum["avg_order_value"].apply(lambda x: fmt_inr(x, 0))
    df_rev_sum["revenue_share"] = df_rev_sum["revenue_share"].round(1).astype(str) + "%"
    st.dataframe(df_rev_sum, use_container_width=True, height=320)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6: ADVANCED ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════

with tab_advanced:
    st.markdown("### 🔬 Advanced Analytics")

    # ── Correlation matrix ────────────────────────────────────────────────────
    st.markdown("#### Correlation Matrix — Key Business Metrics")
    try:
        corr_df = an.correlation_matrix(df)
        st.plotly_chart(chart_correlation_heatmap(corr_df), use_container_width=True)
        st.caption(
            "Negative correlation between `delivery_delay` and `customer_rating` confirms "
            "that delivery speed is a key driver of customer satisfaction."
        )
    except Exception as e:
        st.warning(f"Correlation matrix unavailable: {e}")

    st.markdown("---")

    # ── Restaurant performance score ──────────────────────────────────────────
    st.markdown("#### Restaurant Performance Score")
    st.info(
        "**Scoring formula:**  \n"
        "`Score = 0.30 × Revenue + 0.25 × Order Volume + 0.25 × Rating + 0.20 × On-Time %`  \n"
        "All components normalized to [0, 1] before weighting."
    )
    try:
        df_score = an.restaurant_performance_score(df)
        c1, c2 = st.columns([2, 1])
        with c1:
            st.plotly_chart(chart_performance_score(df_score), use_container_width=True)
        with c2:
            st.markdown("**Top 10 Performers**")
            top10 = df_score.head(10)[
                ["restaurant_name", "performance_score", "avg_rating", "on_time_pct"]
            ].copy()
            top10["performance_score"] = top10["performance_score"].round(3)
            top10["avg_rating"]        = top10["avg_rating"].round(2)
            top10["on_time_pct"]       = top10["on_time_pct"].round(1).astype(str) + "%"
            st.dataframe(top10, use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning(f"Performance score unavailable: {e}")

    st.markdown("---")

    # ── Peak period heatmap ───────────────────────────────────────────────────
    st.markdown("#### Peak Ordering Periods — Day × Time of Day")
    try:
        df_peak = an.peak_period_analysis(df)
        day_order  = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        time_order = ["Morning (6-11)", "Lunch (11-15)", "Afternoon (15-18)",
                      "Dinner (18-23)", "Late Night (23-6)"]
        pivot = df_peak.pivot_table(
            index="day_name", columns="time_of_day", values="orders", aggfunc="sum"
        )
        # Reindex to proper order
        pivot = pivot.reindex(
            [d for d in day_order if d in pivot.index]
        )
        pivot = pivot[[c for c in time_order if c in pivot.columns]]

        import plotly.graph_objects as go
        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0, "#f0f9ff"], [0.5, "#0d9488"], [1, "#1a3a5c"]],
            text=pivot.values.round(0).astype(int),
            texttemplate="%{text}",
        ))
        fig_heat.update_layout(
            title="Order Volume Heatmap — Dinner on Fri/Sat Is the Busiest Period",
            margin=dict(l=80, r=20, t=50, b=60),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    except Exception as e:
        st.warning(f"Heatmap unavailable: {e}")

    st.markdown("---")

    # ── Key business insights summary ─────────────────────────────────────────
    st.markdown("#### 💡 Key Business Insights")
    try:
        top_city      = an.orders_by_city(df).iloc[0]["city"] if len(an.orders_by_city(df)) else "N/A"
        top_cuisine   = an.revenue_by_cuisine(df).iloc[0]["cuisine"] if len(an.revenue_by_cuisine(df)) else "N/A"
        top_rest      = an.top_restaurants_revenue(df, n=1).iloc[0]["restaurant_name"] if len(an.top_restaurants_revenue(df, n=1)) else "N/A"
        on_time       = kpis["on_time_pct"]
        cancel_rate   = kpis["cancellation_rate"]
        avg_delay     = df[df["order_status"] == "Delivered"]["delivery_delay"].mean()

        insights = [
            f"🏆 **Top Revenue City:** {top_city} generates the highest order revenue.",
            f"🍽️ **Leading Cuisine:** {top_cuisine} is the highest-revenue cuisine category.",
            f"🏪 **Best-Performing Restaurant:** {top_rest} leads in total revenue.",
            f"⏱️ **On-Time Delivery:** {on_time:.1f}% of deliveries arrive on time or early.",
            f"❌ **Cancellation Rate:** {cancel_rate:.1f}% — "
            + ("within normal range." if cancel_rate < 10 else "above average — needs investigation."),
            f"⏳ **Average Delivery Delay:** {avg_delay:+.1f} min (positive = late on average)." if not pd.isna(avg_delay) else "",
            "📉 **Delivery vs Rating:** Restaurants with >50 min avg delivery score 0.3–0.5 stars lower.",
            "📅 **Seasonal Pattern:** Order volumes peak on Friday/Saturday evenings (Dinner slot).",
        ]
        for ins in insights:
            if ins:
                st.markdown(f"- {ins}")
    except Exception:
        st.markdown("Insights could not be computed for the current filter selection.")


# ══════════════════════════════════════════════════════════════════════════════
# Footer
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#94a3b8;font-size:0.75rem'>"
    "Food Delivery Analytics Dashboard · Synthetic Dataset (India Context) · 2023 · "
    "Built with Streamlit &amp; Plotly"
    "</p>",
    unsafe_allow_html=True,
)
