# Methodology — Food Delivery Analytics

> **Project:** Food Delivery Analytics Dashboard  
> **Version:** 1.0  
> **Context:** End-to-end data analytics pipeline for a synthetic Indian food-delivery dataset

---

## 1. Dataset Creation

### Source
The dataset is **fully synthetic** — generated programmatically using `src/data_generation.py`.

### Design Goals
- Realistic statistical distributions (not trivially random)
- Meaningful relationships between variables (e.g., delivery time → rating)
- Controlled missing values to demonstrate data cleaning
- Representative of Indian food-delivery market dynamics (6 major cities, 12 cuisine types)

### Generation Approach

| Element | Method |
|---|---|
| Restaurants (60) | Randomly combined prefix + suffix names; each assigned a cuisine, city, quality tier, and pricing |
| Orders (10,000+) | Generated per-day with seasonal and day-of-week multipliers; Poisson-distributed order counts |
| Customer IDs | Power-law repeat-ordering (realistic customer frequency distribution) |
| Restaurant selection | Popularity-weighted (more popular restaurants get more orders) |
| Order amounts | Restaurant base price × number of items × random variance |
| Delivery times | Base formula: 25 + 2.5 × distance + noise; adjusted for peak hours |
| Customer ratings | Derived from restaurant quality tier minus delivery delay penalty plus noise |
| Cancellations | ~8% of orders randomly assigned as Cancelled |
| Missing values | Controlled: ~2% ratings missing, ~1% delivery_partner_id missing, ~0.5% distance missing |
| Duplicates | ~0.3% duplicate rows introduced intentionally for cleaning demonstration |

### Reproducibility
The generator uses `SEED = 42` for all random operations. Re-running `python src/data_generation.py` will always produce the identical dataset.

---

## 2. Data Cleaning

Implemented in `src/data_cleaning.py`. The pipeline applies 9 ordered steps:

### Step 1: Data Type Fixing
- `order_date` → `datetime64`
- `order_time` → `datetime64` (combined with date)
- Numeric columns → `float64` / `int64` via `pd.to_numeric(errors='coerce')`
- String columns → `category` for memory efficiency

### Step 2: Duplicate Removal
- Strategy: `drop_duplicates(subset='order_id', keep='first')`
- Rationale: Order ID is the natural primary key; first occurrence is kept as authoritative

### Step 3: Missing Value Handling

| Column | Strategy | Justification |
|---|---|---|
| `customer_rating` | **Keep NaN** | Absence is meaningful: cancelled orders have no rating; some delivered orders were not rated |
| `delivery_partner_id` | **Fill 'UNKNOWN'** | Imputation is not possible without domain data; marker preserves the information gap |
| `distance_km` | **Impute with city-level median** | Distance is needed for analysis; city-level median is the best available proxy |
| `order_date` | **Drop row** | Temporal information is non-negotiable; <0.01% of rows affected |

### Step 4: Rating Validation
- Ratings outside [1.0, 5.0] are set to `NaN`
- Rationale: Out-of-range ratings indicate data entry errors and must not skew statistics

### Step 5: Amount Validation
- Rows with `order_amount ≤ 0` or `final_amount < 0` are dropped
- Rationale: Non-positive order amounts indicate corrupt records

### Step 6: Delivery Time Validation
- Negative `actual_delivery_time` for Delivered/Pending orders is set to `NaN`
- Rationale: Negative delivery time is physically impossible

### Step 7: Outlier Capping (IQR Method)
- **Method:** Winsorization using Tukey fences with factor = 3.0
- **Formula:** Lower fence = Q1 − 3×IQR; Upper fence = Q3 + 3×IQR
- **Applied to:** `order_amount`, `final_amount`, `delivery_time_minutes`, `distance_km`
- **Factor choice:** 3.0 is more conservative than the standard 1.5 — it only caps extreme outliers while preserving natural distribution variation

### Step 8: Feature Engineering
See Section 4 below.

### Step 9: Sort & Save
Dataset sorted chronologically and saved to `data/processed/cleaned_food_delivery_orders.csv`.

---

## 3. Revenue Calculation

```
gross_order_value = order_amount + delivery_fee
final_amount      = gross_order_value − discount
net_revenue       = final_amount  (only for order_status = "Delivered")
```

**Notes:**
- Cancelled orders contribute ₹0 to net_revenue
- Pending orders are not counted as revenue until confirmed
- This model does not deduct delivery partner payouts (a simplification for analytics purposes)
- All monetary values are in Indian Rupees (₹)

---

## 4. Feature Engineering

New columns created in `engineer_features()`:

| Column | Formula | Notes |
|---|---|---|
| `order_month` | `order_date.dt.month` | Integer 1–12 |
| `order_year` | `order_date.dt.year` | Integer |
| `order_day` | `order_date.dt.day` | Integer 1–31 |
| `day_of_week` | `order_date.dt.dayofweek` | 0=Monday, 6=Sunday |
| `order_hour` | `order_time.dt.hour` | Integer 0–23 |
| `month_name` | `order_date.dt.strftime("%b")` | e.g. "Jan" |
| `day_name` | `order_date.dt.strftime("%A")` | e.g. "Monday" |
| `week_number` | ISO week | Integer 1–53 |
| `is_weekend` | `day_of_week ∈ {5,6}` | Boolean |
| `net_revenue` | `final_amount` if Delivered else 0 | Realized revenue |
| `delivery_delay` | `actual − estimated` | Positive = late |
| `delivery_performance` | Category based on `delivery_delay` | 3-tier |
| `rating_category` | Ordinal bins on `customer_rating` | 4-tier + "Not Rated" |
| `order_value_segment` | `pd.cut` on `final_amount` | 5-tier |
| `time_of_day` | Hour-bucket mapping | 5-tier |

---

## 5. KPI Definitions

| KPI | Formula | Scope |
|---|---|---|
| Total Orders | `COUNT(order_id)` | All statuses |
| Completed Orders | `COUNT(order_id WHERE order_status = "Delivered")` | Delivered only |
| Total Revenue | `SUM(final_amount WHERE order_status = "Delivered")` | Delivered only |
| Avg Order Value | `AVG(final_amount WHERE order_status = "Delivered")` | Delivered only |
| Avg Rating | `AVG(customer_rating)` | All rated orders |
| Avg Delivery Time | `AVG(delivery_time_minutes WHERE order_status = "Delivered")` | Delivered only |
| On-Time % | `COUNT(delivery_delay ≤ 0) / COUNT(Delivered) × 100` | Delivered only |
| Cancellation Rate | `COUNT(Cancelled) / COUNT(All) × 100` | All orders |

---

## 6. Restaurant Performance Score

### Formula
```
Score = 0.30 × revenue_norm
       + 0.25 × order_volume_norm
       + 0.25 × rating_norm
       + 0.20 × on_time_pct_norm
```

### Normalization
Each component is **min-max normalized** to [0, 1]:
```
normalized = (value − min) / (max − min)
```

### Weight Rationale
| Component | Weight | Rationale |
|---|---|---|
| Revenue | 30% | Revenue is the primary business objective |
| Order Volume | 25% | Volume drives platform scale and customer reach |
| Rating | 25% | Customer satisfaction is equally important for retention |
| On-Time % | 20% | Delivery performance directly impacts satisfaction |

### Minimum Threshold
Only restaurants with ≥ 20 delivered orders are included to avoid statistical noise from low-volume restaurants.

---

## 7. Analytical Methodology

### Trend Analysis
- Time-series aggregated at weekly frequency using `pandas.DataFrame.resample('W')`
- Monthly aggregation uses `month_name` categorical ordering for correct calendar sort

### Correlation Analysis
- Pearson correlation coefficient using `pandas.DataFrame.corr()`
- Applied to: order_amount, final_amount, delivery_time_minutes, delivery_delay, customer_rating, distance_km, number_of_items, discount

### Delivery Performance Classification

| Category | Condition |
|---|---|
| Early/On Time | `delivery_delay ≤ 0` |
| Slightly Delayed | `0 < delivery_delay ≤ 10` |
| Significantly Delayed | `delivery_delay > 10` |
| N/A | Cancelled orders or missing data |

### Outlier Detection
- IQR method: `lower = Q1 − 3×IQR`, `upper = Q3 + 3×IQR`
- Values beyond fences are capped (Winsorized) rather than dropped
- Factor 3.0 used to preserve realistic extreme values

---

## 8. Dashboard Methodology

### Technology
- **Streamlit** for the interactive web interface
- **Plotly** for all interactive charts
- **Pandas** for data aggregation
- **Custom CSS** for professional styling

### Filtering Architecture
- All filters applied via `apply_filters()` function before any aggregation
- Filters cascade: later filters act on already-filtered data
- Charts dynamically re-render when filters change (Streamlit's reactive model)

### Chart Design Principles
- Every chart answers a specific business question (stated in the title)
- Titles communicate the insight, not just the dimension (e.g., "Longer Delivery Times Correlate with Lower Ratings" rather than "Rating by Delivery Time")
- Color palette is consistent: navy blue = primary, teal = secondary, orange = accent, green = positive, red = negative
- Pie charts used minimally (only for proportional breakdowns with ≤5 categories)

---

## 9. Reproducibility

The project is fully reproducible from scratch:

```bash
# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Generate raw dataset
python src/data_generation.py

# Step 3: Run cleaning pipeline
python src/data_cleaning.py

# Step 4: Launch dashboard
streamlit run dashboard/app.py

# Step 5: Run tests
pytest tests/
```

All random operations use `SEED = 42` for reproducibility.

---

*Author: Food Delivery Analytics Project | Version 1.0 | 2023*
