# 📊 Zara Sales Analytics Dashboard & Telemetry Platform

> A production-ready, full-stack ecommerce sales analytics suite. Built with a high-performance **FastAPI** analytics engine and a modern **React + Vite + Tailwind CSS** executive dashboard.

[![Tests](https://img.shields.io/badge/pytest-31%2F31%20passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](requirements.txt)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.129-009688)](main.py)
[![React](https://img.shields.io/badge/React-18-61DAFB)](frontend/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v3-38B2AC)](frontend/tailwind.config.js)

---

## 🌟 Highlights

- **Executive KPI Cards**: Real-time Total Revenue, Units Sold, Active Catalog Products, Average Price, and Average Order Value (AOV).
- **Interactive Trend Analytics**: Custom responsive SVG line & area charts with daily/monthly interval toggles and single-day snapshot beacons.
- **Category Performance Breakdown**: Interactive SVG donut chart and progress bars with revenue share percentages.
- **Top Product Rankings**: Leaderboard sorted by revenue or volume sold with visual benchmarks.
- **Transactional Data Explorer**: Searchable, filterable raw sales records with client-side CSV export and pagination.
- **Multi-Dataset Support**: Seamless hot-swapping between the scraped **Zara Dataset (251 products)** and an expanded **15-Month Multi-Year Dataset (3,000 transactions)**.
- **Single-Port Production Serving**: FastAPI serves the pre-built React SPA static assets directly on port 8000.
- **Comprehensive Pytest Suite**: 31 unit, edge-case, and API integration tests covering 100% of the core analytics engine.

---

## 🗂️ Project Architecture

```
zara_dashboard/
│
├── 🚀 start.bat                  # 1-click Windows launcher (starts backend & frontend)
├── 🚀 start.ps1                  # PowerShell launcher script
│
├── 📄 main.py                    # FastAPI REST API + React SPA static file server
├── 📄 analytics.py               # Pure Python analytics engine (KPIs, trends, rankings)
├── 📄 data_loader.py             # CSV pipeline with auto-delimiter detection & cleaning
├── 📄 generate_sample_data.py    # Generator for multi-month realistic retail sales
├── 📄 analysis.py                # Exploratory data helper
├── 📄 requirements.txt           # Python backend dependencies
├── 📄 conftest.py                # Pytest path and shared fixtures configuration
├── 📄 pytest.ini                 # Pytest runner settings
├── 📄 .gitignore                 # Excludes secrets, .env, and node_modules
│
├── 📊 zara.csv                   # Original Zara scrape dataset (251 items)
├── 📊 sample_sales_data.csv      # Multi-month synthetic dataset (3,000 records)
│
├── 📂 tests/                     # 31 Automated Pytest Suites
│   ├── test_analytics.py         # Unit tests for calculations, metrics & aggregations
│   ├── test_api.py               # Integration tests for all REST endpoints & status codes
│   ├── test_data_loader.py       # Data cleaning, normalization, and delimiter tests
│   └── test_sample_generator.py  # Synthetic data generation tests
│
└── 📂 frontend/                  # React 18 + Vite + Tailwind CSS Dashboard
    ├── package.json
    ├── vite.config.js            # Dev proxy config
    ├── tailwind.config.js
    ├── 📂 src/
    │   ├── App.jsx               # Dashboard root, global filters, and state sync
    │   ├── main.jsx              # DOM entrypoint
    │   ├── index.css             # Tailwind base & dark theme styling
    │   └── 📂 components/
    │       ├── MetricCard.jsx    # Glassmorphism KPI cards with trend indicators
    │       ├── TrendChart.jsx    # SVG line & area chart with hover tooltips
    │       ├── CategoryChart.jsx # SVG donut breakdown & category distribution
    │       ├── ProductRanking.jsx# Ranked leaderboard with visual bars
    │       └── DataTable.jsx     # Paginated table, live search & CSV exporter
    └── 📂 dist/                  # Production-optimized SPA bundle
```

---

## 📦 Datasets Included

### 1. `zara.csv` (Original Zara Catalog Scrape)
* **Records**: 251 clothing items scraped from Zara on `2024-02-19`.
* **Total Value**: **$38,751,374.48** in inventory across **457,735 units**.
* **Categories**: Jackets (68.0%), Sweaters (10.6%), Shoes (9.7%), T-Shirts (9.5%), Jeans (2.2%).
* **Format**: Semicolon-separated values (automatically detected by `data_loader.py`).

### 2. `sample_sales_data.csv` (15-Month Multi-Year Simulation)
* **Records**: 3,000 transactions spanning **January 2023 through March 2024**.
* **Total Revenue**: **$16,271,946.37** across **165,485 units sold**.
* **Features**: Seasonal holiday demand multipliers (Q4 Black Friday boosts & summer clearance sales).

---

## 🚀 Quick Start Guide

### Option 1: 1-Click Launch (Windows)
Double-click [`start.bat`](start.bat) in the root directory. It automatically opens both the FastAPI backend and frontend.

---

### Option 2: Run via Terminal

#### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 2: Start the FastAPI Backend
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
* **Dashboard (Production Single-Port Mode)**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

#### Step 3: Run Frontend in Dev Mode (Optional)
```bash
cd frontend
npm install
npm run dev
```
* **Vite Hot-Reload Server**: [http://localhost:3000](http://localhost:3000)

---

## 📡 REST API Reference

| Method | Endpoint | Description | Query Parameters |
|---|---|---|---|
| `GET` | `/health` | Service health status & active dataset | &mdash; |
| `GET` | `/analytics/overview` | High-level KPI summary | `start_date`, `end_date` |
| `GET` | `/analytics/sales-by-product` | Top performing products | `limit` (1-50), `sort_by` (`revenue` \| `quantity_sold`) |
| `GET` | `/analytics/sales-by-category` | Category revenue breakdown | `start_date`, `end_date` |
| `GET` | `/analytics/sales-trend` | Time-series aggregations | `interval` (`daily` \| `monthly`), `start_date`, `end_date` |
| `GET` | `/analytics/raw-sales` | Paginated itemized records | `limit` (1-100), `offset` (≥0) |
| `GET` | `/analytics/filters` | Dynamic date ranges & categories | &mdash; |
| `GET` | `/analytics/datasets` | List available CSV datasets | &mdash; |
| `POST` | `/analytics/switch-dataset` | Live hot-swap active dataset | Body: `{"dataset_name": "zara.csv"}` |

---

## 🧪 Running the Test Suite

Run all automated unit and integration tests with `pytest`:

```bash
python -m pytest
```

### Test Coverage Summary:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
collected 31 items

tests/test_analytics.py ..........                                       [ 32%]
tests/test_api.py ..............                                         [ 77%]
tests/test_data_loader.py ......                                         [ 96%]
tests/test_sample_generator.py .                                         [100%]

============================= 31 passed in 4.95s ==============================
```

---

## 🔒 Security & Environment

* No credentials or `.env` files are tracked in this repository.
* Strict `.gitignore` rules prevent accidentally committing secret keys, virtual environments, or `node_modules/`.

---

## 📄 License

MIT License. Open-source for personal and educational analytics projects.
