# 🍱 Food Delivery Analytics Dashboard

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?logo=streamlit)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.x-blue?logo=plotly)](https://plotly.com)
[![Pandas](https://img.shields.io/badge/Pandas-2.x-darkblue?logo=pandas)](https://pandas.pydata.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

An end-to-end **data analytics course project** that analyzes food delivery operations across 6 Indian cities — from raw data generation through cleaning, EDA, and an interactive Streamlit dashboard.

---

## 📌 Business Problem

Food delivery platforms generate enormous transaction data but often lack structured analytical frameworks to answer critical questions:

- Which restaurants drive the most revenue and why?
- How does delivery speed affect customer satisfaction?
- When and where is demand highest?
- Which operational improvements will have the greatest customer impact?

This project builds a complete analytics pipeline to answer these questions.

---

## 🎯 Objectives

1. Generate a realistic, production-quality synthetic food-delivery dataset
2. Apply a full data cleaning and feature engineering pipeline
3. Conduct in-depth exploratory data analysis (EDA)
4. Build an interactive multi-tab analytics dashboard
5. Derive actionable business insights and recommendations
6. Demonstrate the complete data analytics lifecycle

---

## 📊 Dataset

| Attribute | Value |
|---|---|
| **Records** | ~10,353 orders |
| **Period** | January–December 2023 |
| **Cities** | Mumbai, Delhi, Bengaluru, Hyderabad, Chennai, Pune |
| **Restaurants** | 60 fictional restaurants |
| **Cuisine Types** | 12 categories |
| **Customers** | 3,000 unique customers |
| **Columns (raw)** | 23 |
| **Columns (processed)** | 38 (includes 15 engineered features) |

The dataset is **fully synthetic** but uses realistic statistical distributions, power-law customer behavior, seasonal demand variation, and a designed correlation between delivery delay and customer ratings.

See [`reports/data_dictionary.md`](reports/data_dictionary.md) for full column documentation.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Data Manipulation | Pandas, NumPy |
| Visualization | Plotly, Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Notebooks | Jupyter |
| Testing | Pytest |
| Version Control | Git / GitHub |

---

## 📁 Project Structure

```
food-delivery-analytics/
│
├── README.md                          # This file
├── LICENSE                            # MIT License
├── .gitignore                         # Git ignore rules
├── requirements.txt                   # Production dependencies
├── requirements-dev.txt               # Development dependencies
├── .env.example                       # Environment variable template
│
├── data/
│   ├── raw/
│   │   └── food_delivery_orders.csv   # Raw synthetic dataset (~10K rows)
│   ├── processed/
│   │   └── cleaned_food_delivery_orders.csv  # Cleaned + engineered dataset
│   └── README.md                      # Data documentation
│
├── notebooks/
│   ├── 01_data_exploration.ipynb      # Initial data inspection
│   ├── 02_data_cleaning.ipynb         # Cleaning pipeline walkthrough
│   ├── 03_exploratory_data_analysis.ipynb  # Detailed EDA
│   └── 04_business_analysis.ipynb     # Business insights & recommendations
│
├── src/
│   ├── __init__.py
│   ├── data_generation.py             # Synthetic dataset generator
│   ├── data_cleaning.py               # Reusable cleaning pipeline
│   ├── analysis.py                    # Analytics functions
│   └── utils.py                       # Shared utilities & helpers
│
├── dashboard/
│   ├── app.py                         # Main Streamlit application
│   ├── components.py                  # Plotly chart builders
│   └── styles.css                     # Custom dashboard CSS
│
├── reports/
│   ├── data_dictionary.md             # Column documentation
│   ├── business_insights.md           # Key findings & recommendations
│   └── methodology.md                 # Technical methodology
│
├── tests/
│   ├── __init__.py
│   └── test_data_pipeline.py          # Automated test suite
│
└── assets/
    └── (dashboard_preview.png)        # Dashboard screenshot (add after launch)
```

---

## 📈 Key KPIs

| KPI | Definition |
|---|---|
| **Total Orders** | Count of all orders in the dataset |
| **Completed Orders** | Orders with status = "Delivered" |
| **Total Revenue** | Sum of `final_amount` for Delivered orders |
| **Avg Order Value** | Mean `final_amount` for Delivered orders |
| **Avg Rating** | Mean `customer_rating` across all rated orders |
| **Avg Delivery Time** | Mean `delivery_time_minutes` for Delivered orders |
| **On-Time %** | % of Delivered orders where `delivery_delay ≤ 0` |
| **Cancellation Rate** | % of all orders with status = "Cancelled" |

---

## 💡 Key Insights

> *Derived from the generated synthetic dataset — see [`reports/business_insights.md`](reports/business_insights.md) for full analysis*

1. **~88.7% of orders are successfully delivered** with a ~8.3% cancellation rate.
2. **Friday and Saturday evenings (18–22h)** are the single highest-demand period — ~30% busier than weekdays.
3. **North Indian cuisine** dominates both order volume and revenue.
4. **Delivery delay is the strongest predictor of customer dissatisfaction** — every additional 10 minutes of delay correlates with a ~0.3-point rating drop.
5. **Top 10 restaurants generate ~30–35% of total revenue** — typical marketplace concentration.
6. The platform **systematically under-estimates delivery times** by ~5–8 minutes on average.
7. **UPI accounts for ~35% of payments**, consistent with India's digital payments growth.
8. **Biryani and Continental cuisine** have the highest average order values and ratings despite lower volume.

---

## 🚀 Installation

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/food-delivery-analytics.git
cd food-delivery-analytics

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Run the Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard opens at **http://localhost:8501** in your browser.

### Dashboard Features
- 📊 **6 tabs**: Overview, Restaurants, Delivery, Ratings, Revenue, Advanced Analytics
- 🔍 **Interactive filters**: Date range, City, Cuisine, Order Status, Payment Method, Rating range
- 📦 **8 KPI cards** at the top with live filter updates
- 📈 **25+ interactive Plotly charts**
- 🔬 **Advanced analytics**: Correlation matrix, Performance Score, Peak-Period Heatmap

---

## ⚙️ Run the Data Pipeline

### Generate raw dataset from scratch

```bash
python src/data_generation.py
```

Outputs: `data/raw/food_delivery_orders.csv` (~10,353 rows)

### Run cleaning pipeline

```bash
python src/data_cleaning.py
```

Outputs: `data/processed/cleaned_food_delivery_orders.csv` (38 columns including engineered features)

---

## 📓 Run the Notebooks

```bash
jupyter notebook notebooks/
```

Open notebooks in order:
1. `01_data_exploration.ipynb`
2. `02_data_cleaning.ipynb`
3. `03_exploratory_data_analysis.ipynb`
4. `04_business_analysis.ipynb`

---

## 🧪 Run Tests

```bash
pytest tests/ -v
```

Tests cover:
- Dataset file existence and structure
- Required columns presence
- Order ID uniqueness
- Rating range validation
- Revenue calculation consistency
- Delivery time validity
- Cleaning pipeline end-to-end

---

## 📚 Documentation

| Document | Description |
|---|---|
| [`reports/data_dictionary.md`](reports/data_dictionary.md) | All column definitions, types, and business meaning |
| [`reports/business_insights.md`](reports/business_insights.md) | Key findings and actionable recommendations |
| [`reports/methodology.md`](reports/methodology.md) | Technical methodology: data generation, cleaning, scoring |
| [`data/README.md`](data/README.md) | Dataset overview and file descriptions |

---

## 🔮 Future Improvements

- [ ] Add customer segmentation analysis (RFM model)
- [ ] Implement time-series forecasting for order volume
- [ ] Add delivery partner performance analysis tab
- [ ] Integrate real-time data via API connector
- [ ] Add cohort analysis for customer retention
- [ ] Implement A/B test analysis framework for discount campaigns
- [ ] Add geographic heatmap visualization (folium/kepler.gl)
- [ ] Export reports to PDF from dashboard

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

Built as a **Data Analytics Course Project** to demonstrate the complete analytics lifecycle:

```
Raw Data → Cleaning → EDA → Feature Engineering → Business Analysis → Dashboard → Insights
```

*Dataset is entirely synthetic and modelled on publicly available information about the Indian food-delivery market. No real customer or restaurant data was used.*
