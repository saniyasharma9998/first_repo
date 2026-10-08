"""
data_generation.py
------------------
Generates a realistic synthetic food-delivery dataset for India.

Revenue definition:
  gross_order_value = order_amount + delivery_fee
  final_amount      = gross_order_value - discount
  net_revenue       = final_amount  (platform net after discount, before partner payout)

Run:
    python src/data_generation.py
Outputs:
    data/raw/food_delivery_orders.csv  (~10 000 rows)
"""

import os
import random
from pathlib import Path

import numpy as np
import pandas as pd

# ── Reproducibility ────────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ── Output path ────────────────────────────────────────────────────────────────
OUTPUT_PATH = Path("data/raw/food_delivery_orders.csv")

# ── Constants ──────────────────────────────────────────────────────────────────
N_ORDERS = 10_500          # slight over-generation; duplicates introduced later
N_CUSTOMERS = 3_000
N_RESTAURANTS = 60
N_DELIVERY_PARTNERS = 250

START_DATE = pd.Timestamp("2023-01-01")
END_DATE   = pd.Timestamp("2023-12-31")

# ── Cities and areas ───────────────────────────────────────────────────────────
CITIES = {
    "Mumbai":    ["Andheri", "Bandra", "Dadar", "Juhu", "Powai", "Thane", "Borivali"],
    "Delhi":     ["Connaught Place", "Dwarka", "Lajpat Nagar", "Rohini", "Saket", "Vasant Kunj"],
    "Bengaluru": ["Indiranagar", "Koramangala", "Whitefield", "HSR Layout", "Jayanagar", "Marathahalli"],
    "Hyderabad": ["Banjara Hills", "Gachibowli", "Hitech City", "Jubilee Hills", "Madhapur"],
    "Chennai":   ["Adyar", "Anna Nagar", "Nungambakkam", "T Nagar", "Velachery"],
    "Pune":      ["Aundh", "Baner", "Hadapsar", "Kothrud", "Viman Nagar"],
}
CITY_WEIGHTS = [0.22, 0.20, 0.20, 0.15, 0.13, 0.10]   # population-weighted

# ── Cuisine types ──────────────────────────────────────────────────────────────
CUISINES = [
    "North Indian", "South Indian", "Chinese", "Fast Food",
    "Pizza", "Biryani", "Desserts", "Beverages",
    "Continental", "Street Food", "Seafood", "Mughlai",
]
CUISINE_WEIGHTS = [0.18, 0.13, 0.14, 0.12, 0.10, 0.09, 0.05, 0.04, 0.05, 0.06, 0.02, 0.02]

# ── Payment methods ────────────────────────────────────────────────────────────
PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Cash on Delivery", "Wallet"]
PAYMENT_WEIGHTS = [0.35, 0.22, 0.18, 0.15, 0.10]

# ── Restaurant name components ─────────────────────────────────────────────────
REST_PREFIXES  = ["Spice", "Royal", "Golden", "Urban", "The", "Desi", "Masala",
                  "Saffron", "Tandoor", "Punjabi", "Hyderabadi", "Mumbai", "Delhi",
                  "Coastal", "Flame", "Curry", "Zesty", "Chai", "The Authentic", "Gourmet"]
REST_SUFFIXES  = ["Kitchen", "Grill", "House", "Bites", "Express", "Hut",
                  "Corner", "Dhaba", "Palace", "Cafe", "Restaurant", "Hub",
                  "Junction", "Station", "Garden", "Lounge", "Pavilion", "Co."]

# ── Order-hour distribution (bell around lunch/dinner) ─────────────────────────
def _order_hour_distribution() -> np.ndarray:
    """Returns probability weights for each hour 0-23."""
    weights = np.zeros(24)
    # Lunch peak  11-14
    for h in range(11, 15):
        weights[h] += np.exp(-0.5 * ((h - 12.5) / 1.2) ** 2)
    # Dinner peak 18-22
    for h in range(18, 23):
        weights[h] += 1.2 * np.exp(-0.5 * ((h - 20) / 1.5) ** 2)
    # Late-night trickle
    weights[23] += 0.05
    weights[0]  += 0.03
    weights[1]  += 0.01
    return weights / weights.sum()

HOUR_WEIGHTS = _order_hour_distribution()

# ── Day-of-week multipliers (Fri/Sat/Sun busier) ───────────────────────────────
DOW_MULTIPLIERS = {0: 0.85, 1: 0.80, 2: 0.85, 3: 0.90, 4: 1.10, 5: 1.30, 6: 1.20}


# ══════════════════════════════════════════════════════════════════════════════
# Helper generators
# ══════════════════════════════════════════════════════════════════════════════

def _generate_restaurant_pool(n: int) -> pd.DataFrame:
    """Create a pool of fictional restaurants with stable properties."""
    names_seen: set = set()
    rows = []
    cuisine_list = random.choices(CUISINES, weights=CUISINE_WEIGHTS, k=n * 3)
    ci = 0
    r_id = 1
    while len(rows) < n:
        cuisine = cuisine_list[ci]; ci += 1
        prefix  = random.choice(REST_PREFIXES)
        suffix  = random.choice(REST_SUFFIXES)
        name    = f"{prefix} {suffix}"
        if name in names_seen:
            continue
        names_seen.add(name)
        # Each restaurant has a baseline avg order size and quality tier
        quality    = np.clip(np.random.normal(3.8, 0.5), 2.0, 5.0)
        avg_items  = random.randint(2, 5)
        base_price = random.choice([150, 180, 220, 260, 300, 350, 400])  # per-item price
        city       = random.choices(list(CITIES.keys()), weights=CITY_WEIGHTS)[0]
        area       = random.choice(CITIES[city])
        rows.append({
            "restaurant_id":   f"R{r_id:03d}",
            "restaurant_name": name,
            "cuisine":         cuisine,
            "rest_city":       city,
            "rest_area":       area,
            "quality_tier":    quality,
            "avg_items":       avg_items,
            "base_price":      base_price,
        })
        r_id += 1
    return pd.DataFrame(rows)


def _generate_orders(restaurants: pd.DataFrame) -> pd.DataFrame:
    """Generate the main orders DataFrame."""
    rng = np.random.default_rng(SEED)

    # ── Date/time allocation ──────────────────────────────────────────────────
    date_range = pd.date_range(START_DATE, END_DATE, freq="D")
    # Assign order counts per day with seasonal variation
    base_orders_per_day = N_ORDERS / len(date_range)
    day_counts = []
    for d in date_range:
        dow_mult   = DOW_MULTIPLIERS[d.dayofweek]
        month_mult = 1.0 + 0.15 * np.sin((d.month - 1) * np.pi / 6)  # mild seasonality
        expected   = base_orders_per_day * dow_mult * month_mult
        count      = max(0, int(rng.poisson(expected)))
        day_counts.append((d, count))

    # Flatten to a list of (date, hour)
    dates_hours = []
    for d, cnt in day_counts:
        hours = rng.choice(24, size=cnt, p=HOUR_WEIGHTS)
        for h in hours:
            dates_hours.append((d, int(h)))
    random.shuffle(dates_hours)

    total = len(dates_hours)

    # ── Customer IDs ──────────────────────────────────────────────────────────
    # Some customers are repeat orderers
    customer_ids = [f"C{i:05d}" for i in range(1, N_CUSTOMERS + 1)]
    # Power-law repeat purchasing
    customer_weights = 1.0 / (np.arange(1, N_CUSTOMERS + 1) ** 0.7)
    customer_weights /= customer_weights.sum()
    assigned_customers = rng.choice(customer_ids, size=total, p=customer_weights)

    # ── Restaurant IDs ────────────────────────────────────────────────────────
    rest_ids     = restaurants["restaurant_id"].values
    rest_weights = 1.0 / (np.arange(1, len(rest_ids) + 1) ** 0.5)  # popular restaurants get more
    rest_weights /= rest_weights.sum()
    assigned_rests = rng.choice(len(rest_ids), size=total, p=rest_weights)

    # ── Delivery partners ─────────────────────────────────────────────────────
    partner_ids = [f"DP{i:04d}" for i in range(1, N_DELIVERY_PARTNERS + 1)]
    assigned_partners = rng.choice(partner_ids, size=total)

    # ── Order status (realistic cancellation ~8%) ─────────────────────────────
    statuses       = ["Delivered", "Cancelled", "Pending"]
    status_weights = [0.89, 0.08, 0.03]
    assigned_status = random.choices(statuses, weights=status_weights, k=total)

    # ── Build rows ────────────────────────────────────────────────────────────
    rows = []
    for i in range(total):
        d, h       = dates_hours[i]
        r_idx      = assigned_rests[i]
        rest       = restaurants.iloc[r_idx]
        status     = assigned_status[i]

        # Minute
        minute = rng.integers(0, 60)
        order_dt = d + pd.Timedelta(hours=int(h), minutes=int(minute))

        # Number of items
        n_items = max(1, int(rng.normal(rest["avg_items"], 1.2)))

        # Order amount (item prices + some variance)
        unit_price   = rest["base_price"] * rng.uniform(0.85, 1.20)
        order_amount = round(n_items * unit_price, 2)

        # Delivery fee (free above threshold)
        if order_amount >= 500:
            delivery_fee = 0.0
        else:
            delivery_fee = round(random.choice([20, 25, 30, 35, 40, 45, 50]), 2)

        # Discount (coupon ~30% of orders)
        has_discount = rng.random() < 0.30
        if has_discount:
            disc_pct  = rng.choice([5, 10, 15, 20, 25, 30])
            discount  = round(order_amount * disc_pct / 100, 2)
        else:
            discount = 0.0

        gross_order_value = round(order_amount + delivery_fee, 2)
        final_amount      = round(max(0, gross_order_value - discount), 2)

        # Distance
        distance_km = round(rng.uniform(0.5, 15.0), 2)

        # Estimated delivery time (mins): base 25 + 2*distance + noise
        est_delivery = int(25 + 2.5 * distance_km + rng.normal(0, 5))
        est_delivery = max(15, min(90, est_delivery))

        # Actual delivery time
        if status == "Cancelled":
            actual_delivery    = None
            delivery_time_mins = None
            rating             = None
        else:
            # Quality tier affects delivery performance
            quality_factor = rest["quality_tier"]
            # Busy hours have longer delivery
            busy_hour = 1.2 if h in range(12, 14) or h in range(19, 22) else 1.0
            delay_bias = rng.normal(2, 8)   # slight positive bias = usually a bit late
            actual_delivery = int(est_delivery * busy_hour + delay_bias)
            actual_delivery = max(10, min(120, actual_delivery))
            delivery_time_mins = actual_delivery

            # Rating: negatively correlated with delivery delay, positively with quality
            base_rating = quality_factor
            delay_penalty = max(0, (actual_delivery - est_delivery)) * 0.03
            raw_rating = base_rating - delay_penalty + rng.normal(0, 0.4)
            rating = round(np.clip(raw_rating, 1.0, 5.0) * 2) / 2   # round to 0.5

        payment = random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS)[0]

        rows.append({
            "order_id":                f"ORD{i+1:06d}",
            "order_date":              d.date(),
            "order_time":              order_dt.strftime("%H:%M:%S"),
            "customer_id":             assigned_customers[i],
            "restaurant_id":           rest["restaurant_id"],
            "restaurant_name":         rest["restaurant_name"],
            "cuisine":                 rest["cuisine"],
            "city":                    rest["rest_city"],
            "area":                    rest["rest_area"],
            "order_amount":            order_amount,
            "delivery_fee":            delivery_fee,
            "discount":                discount,
            "gross_order_value":       gross_order_value,
            "final_amount":            final_amount,
            "payment_method":          payment,
            "order_status":            status,
            "delivery_partner_id":     assigned_partners[i],
            "estimated_delivery_time": est_delivery,
            "actual_delivery_time":    actual_delivery,
            "delivery_time_minutes":   delivery_time_mins,
            "customer_rating":         rating,
            "number_of_items":         n_items,
            "distance_km":             distance_km,
        })

    df = pd.DataFrame(rows)

    # ── Introduce controlled missing values ───────────────────────────────────
    # ~2% missing ratings for delivered orders (forgot to rate)
    delivered_mask = df["order_status"] == "Delivered"
    forget_idx = df[delivered_mask].sample(frac=0.02, random_state=SEED).index
    df.loc[forget_idx, "customer_rating"] = np.nan

    # ~1% missing delivery_partner_id (data entry gap)
    dp_null_idx = df.sample(frac=0.01, random_state=SEED + 1).index
    df.loc[dp_null_idx, "delivery_partner_id"] = np.nan

    # ~0.5% missing distance
    dist_null_idx = df.sample(frac=0.005, random_state=SEED + 2).index
    df.loc[dist_null_idx, "distance_km"] = np.nan

    # ── Introduce a small number of duplicate rows (~0.3%) ────────────────────
    dup_count = max(1, int(total * 0.003))
    dup_rows  = df.sample(n=dup_count, random_state=SEED + 3)
    df = pd.concat([df, dup_rows], ignore_index=True)

    return df


# ══════════════════════════════════════════════════════════════════════════════
# Public entry point
# ══════════════════════════════════════════════════════════════════════════════

def generate_dataset(output_path: str | Path = OUTPUT_PATH, verbose: bool = True) -> pd.DataFrame:
    """
    Generate the synthetic food-delivery dataset and save it to *output_path*.

    Parameters
    ----------
    output_path : str or Path
        Destination CSV file path.
    verbose : bool
        Print progress messages.

    Returns
    -------
    pd.DataFrame
        The generated (unsaved) raw DataFrame.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if verbose:
        print("Generating restaurant pool …")
    restaurants = _generate_restaurant_pool(N_RESTAURANTS)

    if verbose:
        print(f"Generating {N_ORDERS:,} orders …")
    df = _generate_orders(restaurants)

    df.to_csv(output_path, index=False)
    if verbose:
        print(f"✓  Saved {len(df):,} rows → {output_path}")

    return df


if __name__ == "__main__":
    generate_dataset()
