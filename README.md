# 🏥 Ethiopian Medical Data Warehouse

[![CI/CD Pipeline](https://github.com/meleseabrham/week-8-medical-telegram-warehouse/actions/workflows/main.yml/badge.svg)](https://github.com/meleseabrham/week-8-medical-telegram-warehouse/actions)

An end-to-end data engineering pipeline designed to archive, clean, and analyze medical business data from public Ethiopian Telegram channels. This project utilizes a sophisticated ELT stack including **Python**, **YOLOv8 AI**, **PostgreSQL**, **dbt**, **FastAPI**, and **Dagster**.

---

## 🌟 Core Features

- **🚀 Scalable Incremental Scraping**: Smart scraping that only fetches new messages, optimizing resource usage.
- **👁️ YOLOv8 AI Enrichment**: Automatic object detection and image categorization (Promotions, Products, Lifestyle).
- **🏗️ Star Schema Warehouse**: Advanced dbt modeling for pharmaceutical and medical retail analytics.
- **⚡ Analytical API**: High-performance FastAPI endpoints for real-time reporting.
- **🔄 Full Orchestration**: Entire pipeline automated with Dagster (Daily schedules + Job monitoring).
- **📊 Intelligence Dashboard**: Interactive Jupyter notebook for visualizing business insights.

---

## 📂 Project Structure

```text
├── api/                # FastAPI Analytical Layer
├── orchestration/      # Dagster Pipeline Definitions (Jobs, Ops, Schedules)
├── medical_warehouse/  # dbt Project (Transformation Logic)
├── notebooks/          # API Visualization Dashboards
├── src/                # Core Logic (Scraper, Loader, YOLO Detection)
├── data/               
│   ├── raw/            # Scraped JSON & Images (Data Lake)
│   └── processed/      # YOLO Detection CSVs
├── tests/              # API and Pipeline Tests
├── logs/               # Execution audit trails
└── docker-compose.yml  # Database Infrastructure
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Docker (for PostgreSQL)
- Telegram API Credentials ([my.telegram.org](https://my.telegram.org))

### 2. Configure Environment
Create a `.env` file in the root directory:
```env
# Telegram Auth
TG_API_ID=your_id
TG_API_HASH=your_hash

# Database (Default for Docker)
DB_HOST=localhost
DB_PORT=5433
DB_NAME=medical_db
DB_USER=sa
DB_PASS=123
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🏃 How to Run

### **Option 1: Guided Orchestration (Recommended)**
The entire pipeline (Scrape -> Load -> YOLO -> dbt) is managed by Dagster.
```bash
python -m dagster dev -m orchestration
```
Then visit **[http://localhost:3000](http://localhost:3000)** to launch the `medical_pipeline_job`.

### **Option 2: Manual Execution**
If you prefer running individual components:
1. **Scrape Data**: `python src/scraper.py`
2. **Load to SQL**: `python src/load_data.py`
3. **Run AI Detection**: `python src/yolo_detect.py`
4. **dbt Transform**: `cd medical_warehouse && dbt run`
5. **Start API**: `uvicorn api.main:app --reload`

---

## 📈 Analytical API Endpoints
The API serves business insights at `http://localhost:8000/docs`:
- `GET /api/reports/top-products`: Most frequent medical keywords.
- `GET /api/reports/visual-content`: Engagement stats by image category.
- `GET /api/channels/{name}/activity`: Channel-specific performance metrics.
- `GET /api/search/messages`: Full-text search across all collected data.

---

## ✅ Quality & Compliance
- **CI/CD**: Fully passing GitHub Actions on `task-4` and `task-5`.
- **Testing**: Includes `pytest` for API and 15+ dbt tests for data integrity.
- **Scalability**: Implemented state tracking to prevent duplicate processing.

---

## 📝 License
MIT License. Developed for Advanced Data Engineering Research.
