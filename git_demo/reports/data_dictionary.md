# Data Dictionary — Food Delivery Analytics

> **Project:** Food Delivery Analytics Dashboard  
> **Dataset:** `data/raw/food_delivery_orders.csv` (raw) and `data/processed/cleaned_food_delivery_orders.csv` (processed)  
> **Context:** Synthetic dataset modelled on the Indian food-delivery market (2023, 6 cities)

---

## Raw Dataset Columns (23)

| Column | Data Type | Description | Example Value | Business Meaning |
|---|---|---|---|---|
| `order_id` | string | Unique order identifier | `ORD000123` | Primary key for each order transaction |
| `order_date` | date (YYYY-MM-DD) | Calendar date the order was placed | `2023-07-15` | Used for time-series and trend analysis |
| `order_time` | time (HH:MM:SS) | Time of day the order was placed | `19:34:22` | Used for peak-hour analysis |
| `customer_id` | string | Unique customer identifier | `C00042` | Enables repeat-order and customer-segment analysis |
| `restaurant_id` | string | Unique restaurant identifier | `R012` | Links orders to restaurant master data |
| `restaurant_name` | string | Fictional restaurant name | `Spice Kitchen` | Human-readable restaurant label |
| `cuisine` | string/category | Cuisine type of the restaurant | `North Indian` | Cuisine-level revenue and rating analysis |
| `city` | string/category | City where the restaurant is located | `Mumbai` | Geographic performance analysis |
| `area` | string/category | Neighbourhood/area within the city | `Bandra` | Sub-city demand mapping |
| `order_amount` | float (₹) | Gross value of food items ordered (before fee/discount) | `485.50` | Base revenue metric |
| `delivery_fee` | float (₹) | Fee charged for delivery (₹0 if order ≥ ₹500) | `35.00` | Delivery monetization metric |
| `discount` | float (₹) | Coupon/promotional discount applied | `72.75` | Discount impact analysis |
| `gross_order_value` | float (₹) | `order_amount + delivery_fee` | `520.50` | Total customer commitment before discount |
| `final_amount` | float (₹) | `gross_order_value − discount` (amount actually paid) | `447.75` | Net revenue basis; key financial metric |
| `payment_method` | string/category | How the customer paid | `UPI` | Payment preference analysis |
| `order_status` | string/category | Outcome of the order | `Delivered` | Defines completed vs cancelled orders |
| `delivery_partner_id` | string | Identifier of the delivery partner | `DP0123` | Delivery partner performance tracking |
| `estimated_delivery_time` | int (minutes) | Platform's predicted delivery duration | `35` | Benchmark for delivery accuracy |
| `actual_delivery_time` | int (minutes) | Actual door-to-door delivery time | `42` | Measured delivery performance |
| `delivery_time_minutes` | int (minutes) | Alias for `actual_delivery_time` (NULL for cancelled) | `42` | Primary delivery KPI column |
| `customer_rating` | float (1.0–5.0) | Rating given by customer (in 0.5 increments) | `4.0` | Customer satisfaction metric |
| `number_of_items` | int | Number of distinct items in the order | `3` | Order complexity proxy |
| `distance_km` | float (km) | Estimated distance from restaurant to customer | `4.2` | Impacts delivery time and fee |

---

## Derived / Feature-Engineered Columns (15 added in processed dataset)

| Column | Type | Formula / Logic | Example | Business Use |
|---|---|---|---|---|
| `order_month` | int | `order_date.month` | `7` | Monthly trend analysis |
| `order_year` | int | `order_date.year` | `2023` | Year-over-year (future) |
| `order_day` | int | `order_date.day` | `15` | Intra-month patterns |
| `day_of_week` | int (0=Mon) | `order_date.dayofweek` | `4` | Weekday vs weekend |
| `order_hour` | int (0–23) | `order_time.hour` | `19` | Hourly peak analysis |
| `month_name` | string | e.g. `"Jul"` | `Jul` | Readable month labels |
| `day_name` | string | e.g. `"Friday"` | `Friday` | Readable day labels |
| `week_number` | int | ISO week number | `28` | Week-level trends |
| `is_weekend` | bool | True if day_of_week ∈ {5, 6} | `True` | Weekend uplift analysis |
| `net_revenue` | float (₹) | `final_amount` if Delivered, else `0` | `447.75` | Realized revenue (excludes cancelled) |
| `delivery_delay` | float (min) | `actual_delivery_time − estimated_delivery_time` | `+7` | Delivery accuracy metric |
| `delivery_performance` | category | Based on `delivery_delay`: ≤0 → "Early/On Time"; 1–10 → "Slightly Delayed"; >10 → "Significantly Delayed" | `Slightly Delayed` | Performance categorization |
| `rating_category` | category | ≥4.5→Excellent; ≥3.5→Good; ≥2.5→Average; <2.5→Poor | `Good` | Satisfaction segmentation |
| `order_value_segment` | category | Cut: <₹200, ₹200-400, ₹400-700, ₹700-1K, >₹1K | `₹400-700` | Revenue segmentation |
| `time_of_day` | string | Morning 6–11; Lunch 11–15; Afternoon 15–18; Dinner 18–23; Late Night 23–6 | `Dinner (18-23)` | Time-slot analysis |

---

## Revenue Definitions

| Metric | Formula | Notes |
|---|---|---|
| **Gross Order Value** | `order_amount + delivery_fee` | Total customer commitment before discounts |
| **Final Amount** | `gross_order_value − discount` | Actual amount paid by customer |
| **Net Revenue** | `final_amount` where `order_status = "Delivered"` | Platform-realized revenue (cancelled orders = ₹0) |

> **Note:** This model does not deduct delivery-partner payouts (typically 20–25% of final_amount in real platforms). `net_revenue` represents the gross take-rate before partner costs.

---

## Value Sets

| Column | Allowed Values |
|---|---|
| `order_status` | `Delivered`, `Cancelled`, `Pending` |
| `cuisine` | `North Indian`, `South Indian`, `Chinese`, `Fast Food`, `Pizza`, `Biryani`, `Desserts`, `Beverages`, `Continental`, `Street Food`, `Seafood`, `Mughlai` |
| `city` | `Mumbai`, `Delhi`, `Bengaluru`, `Hyderabad`, `Chennai`, `Pune` |
| `payment_method` | `UPI`, `Credit Card`, `Debit Card`, `Cash on Delivery`, `Wallet` |
| `delivery_performance` | `Early/On Time`, `Slightly Delayed`, `Significantly Delayed`, `N/A` |
| `rating_category` | `Excellent`, `Good`, `Average`, `Poor`, `Not Rated` |
| `time_of_day` | `Morning (6-11)`, `Lunch (11-15)`, `Afternoon (15-18)`, `Dinner (18-23)`, `Late Night (23-6)` |

---

*Last updated: 2023 | Author: Food Delivery Analytics Project*
