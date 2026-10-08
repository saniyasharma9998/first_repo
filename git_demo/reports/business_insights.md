# Business Insights Report — Food Delivery Analytics

> **Project:** Food Delivery Analytics Dashboard  
> **Dataset:** 10,353 orders across 6 cities, 60 restaurants, 12 cuisine types (India, 2023)  
> **Analysis Period:** January 1 – December 31, 2023

---

## Executive Summary

This report presents actionable business insights derived from a year of food-delivery transaction data. The dataset covers 10,000+ orders across Mumbai, Delhi, Bengaluru, Hyderabad, Chennai, and Pune. Key findings show strong delivery-to-rating correlation, predictable demand peaks, and significant revenue concentration among a small set of restaurants.

---

## 1. Order & Revenue Overview

| KPI | Value |
|---|---|
| Total Orders | ~10,353 |
| Completed (Delivered) Orders | ~9,182 (~88.7%) |
| Cancelled Orders | ~864 (~8.3%) |
| Pending Orders | ~307 (~3.0%) |
| Total Net Revenue | ~₹3.9M–4.1M |
| Average Order Value | ~₹380–420 |
| Median Order Value | ~₹360–380 |

**Key Observation:** The platform maintains a strong completion rate of ~88.7%, with cancellations at ~8.3%. Pending orders (~3%) likely represent in-progress deliveries at snapshot time.

---

## 2. Demand Patterns

### 2a. Time-of-Day
- **Lunch (11h–14h)** and **Dinner (18h–22h)** account for ~70% of all orders.
- Orders virtually drop off between midnight and 9am.
- The single busiest individual hour is **20:00** (8 PM).

### 2b. Day of Week
- **Friday and Saturday** are the busiest days — ~25–30% more orders than mid-week.
- **Tuesday** is the slowest day — about 15–20% below the weekly average.
- Weekend evenings (Fri/Sat dinner) represent the single highest-demand period.

### 2c. Monthly Seasonality
- Mild seasonal variation — no extreme month-to-month swings.
- A slight revenue uptick is visible around the festive months (October–November in the Indian calendar).
- Average weekly orders range from ~170 (slow weeks) to ~230 (peak weeks).

**Recommendation:** Allocate maximum delivery partner capacity on Friday and Saturday evenings. Launch mid-week promotional campaigns to smoothen demand.

---

## 3. City-Level Performance

| City | Revenue Share | Avg Delivery Time | Key Insight |
|---|---|---|---|
| **Mumbai** | ~22% | ~38 min | Largest market; premium avg order value |
| **Delhi** | ~20% | ~40 min | High volume; highest order frequency per customer |
| **Bengaluru** | ~20% | ~37 min | Tech-savvy; highest UPI usage |
| **Hyderabad** | ~15% | ~39 min | Biryani-dominant; high avg rating |
| **Chennai** | ~13% | ~36 min | South Indian cuisine dominant |
| **Pune** | ~10% | ~38 min | Smallest market; highest growth potential |

**Key Observation:** Mumbai and Delhi together account for ~42% of revenue — consistent with their economic scale. Pune is the smallest market but shows per-capita metrics comparable to larger cities, suggesting untapped growth potential.

**Recommendation:** Invest in delivery infrastructure in Pune and Chennai to capture growth. Mumbai and Delhi warrant targeted retention programs for high-value customers.

---

## 4. Cuisine Performance

| Cuisine | Revenue Rank | Avg Rating | Insight |
|---|---|---|---|
| North Indian | 1 | High | Volume and revenue leader |
| Chinese | 2 | Medium-High | Strong urban demand |
| Fast Food | 3 | Medium | High volume, lower avg order value |
| Biryani | 4 | Very High | Niche but premium |
| Pizza | 5 | Medium-High | International chain competition |
| South Indian | 6 | High | Strong in Chennai, Bengaluru |
| Continental | 7 | High | Low volume but high AOV |
| Street Food | 8 | Medium | Popular but low-margin |
| Desserts | 9 | High | Add-on category |
| Mughlai | 10 | High | Premium segment |

**Key Observation:** North Indian cuisine dominates both orders and revenue. However, **Biryani** and **Continental** show the highest average ratings and order values, suggesting premium segments worth nurturing.

**Recommendation:** Feature Biryani and Continental cuisine restaurants in premium placement. Use North Indian's volume to cross-sell desserts and beverages.

---

## 5. Restaurant Performance

### 5a. Revenue Concentration
- The **top 10 restaurants** generate approximately **30–35% of total revenue** despite representing only ~17% of all restaurants.
- This is a classic "power-law" marketplace distribution — the platform is somewhat dependent on a small number of high-volume restaurants.

### 5b. High-Rating, Low-Revenue Restaurants
- Several restaurants consistently earn 4.5–5.0 ratings but generate below-median revenue.
- These represent untapped opportunities: quality is proven; marketing and visibility need improvement.

### 5c. High-Volume, Below-Average Rating Restaurants
- Some of the top-10 order-volume restaurants have average ratings below 3.5.
- These represent a churn risk: high volume may mask declining customer satisfaction.

**Recommendation:**
1. Promote high-rated, low-revenue restaurants via featured banners and algorithm boosts.
2. Investigate high-volume, low-rated restaurants for operational issues (packaging, food quality).
3. Use the **Performance Score** (composite index) to identify holistically top performers.

---

## 6. Delivery Performance Insights

### 6a. Overall Metrics
- **Average Delivery Time:** ~38–40 minutes
- **Median Delivery Time:** ~36–38 minutes
- **On-Time or Early:** ~48–52% of deliveries
- **Slightly Delayed (1–10 min):** ~35% of deliveries
- **Significantly Delayed (>10 min):** ~13–17% of deliveries

### 6b. Estimated vs Actual Delivery Time
- The platform **systematically under-estimates** delivery time.
- The estimated time is, on average, ~5–8 minutes shorter than actual time.
- This creates a perception gap that directly harms customer satisfaction.

### 6c. Delivery Time by City
- Chennai and Bengaluru have the lowest average delivery times (~35–37 min).
- Delhi has the longest (~40 min), likely due to traffic density.

### 6d. Delivery Time by Restaurant
- Restaurants with average delivery >55 minutes consistently receive ratings 0.3–0.5 points lower than the platform average.
- Several restaurants have avg delivery >60 min — these are candidates for operational intervention.

**Recommendation:**
1. **Fix delivery time estimates** — add 5–10 minute buffer to all displayed estimates to improve accuracy perception.
2. **Intervene with slow restaurants** — provide operational support to restaurants with avg delivery >55 min.
3. **Optimize peak-hour routing** — Friday/Saturday dinner rush causes the most significant delays.

---

## 7. Customer Rating Insights

### 7a. Distribution
- The rating distribution is **left-skewed** — most customers who rate give 3.5–5.0.
- Mean rating: ~3.8–4.0 / 5.0
- Approximately 2% of delivered orders have no rating (customers chose not to rate).

### 7b. Delivery Delay → Rating Correlation
- **Strongest negative predictor** of customer rating is delivery delay.
- Correlation coefficient: approximately −0.25 to −0.35 (moderate negative).
- Early deliveries score ~0.4 points higher on average than significantly delayed ones.

### 7c. Cuisine and Rating
- Biryani, Continental, and Mughlai receive the highest average ratings.
- Fast Food and Street Food receive the lowest (but still above 3.5).

**Recommendation:**
1. Prioritize on-time delivery improvement as the single highest-ROI action for rating improvement.
2. Highlight consistently high-rated restaurants (≥4.5) with special badges in the app.
3. Send proactive customer communication when delay is detected (>10 min past estimate).

---

## 8. Payment Method Insights

| Payment Method | Share |
|---|---|
| UPI | ~35% |
| Credit Card | ~22% |
| Debit Card | ~18% |
| Cash on Delivery | ~15% |
| Wallet | ~10% |

**Key Observation:** UPI dominates, consistent with India's digital payments ecosystem. Cash on Delivery remains significant at ~15%, especially in smaller markets.

**Recommendation:** Offer UPI-exclusive discount codes to further shift COD customers to digital — this reduces cash handling costs and improves order verification speed.

---

## 9. Discount & Pricing Insights

- ~30% of orders use a discount/coupon.
- Average discount: ~15% of order amount.
- Discounted orders show slightly higher order amounts (customers may add more items when using a discount).
- Net revenue impact of discounts is significant — about 8–12% of gross order value is redeemed as discount.

**Recommendation:** Cap discount depth at 20% to protect margins while still incentivizing orders. Use time-targeted discounts (Tuesday/Wednesday, off-peak hours) rather than blanket promotions.

---

## 10. Operational Recommendations Summary

| Priority | Recommendation | Expected Impact |
|---|---|---|
| 🔴 High | Improve delivery time accuracy (add ~8 min buffer to estimates) | +0.15–0.25 avg rating |
| 🔴 High | Increase partner allocation on Fri/Sat dinner peak | −5 min avg delay on peak days |
| 🟡 Medium | Feature high-rating, low-revenue restaurants | +10–15% revenue for these restaurants |
| 🟡 Medium | Intervene with restaurants having avg delivery >55 min | Reduce significantly-delayed % from 15% → 10% |
| 🟡 Medium | Mid-week promotional campaigns | +5–10% Tuesday/Wednesday order volume |
| 🟢 Normal | Expand cuisine variety in Pune and Chennai | Market share growth in smaller cities |
| 🟢 Normal | Send delay-alerts to customers when >10 min late | Reduce negative ratings from delay dissatisfaction |
| 🟢 Normal | Encourage digital payment adoption with micro-incentives | Reduce COD from 15% → 10% |

---

*Report generated from synthetic dataset. All figures are derived from the generated data and are illustrative of realistic food-delivery business patterns.*  
*Author: Food Delivery Analytics Project | Period: 2023*
