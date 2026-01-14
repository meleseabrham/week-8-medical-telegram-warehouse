# 🏥 Ethiopian Medical Business Data Warehouse

An end-to-end data engineering pipeline designed to scrape, clean, and model data from public Telegram channels related to medical businesses in Ethiopia. The project implements a robust ELT (Extract, Load, Transform) architecture using Python, PostgreSQL, and dbt.

---

## 🚀 Project Overview

This system automates the collection of medical business data (posts, images, and metadata) and transforms it into a structured, analytical-ready Star Schema.

### Key Features:
- **Scalable Scraping**: Multi-channel Telegram scraping with automated image downloading.
- **Raw Data Lake**: Partitioned storage for raw JSON metadata and organized image folders.
- **Automated Loading**: Clean Python-based ingestion into a `raw` PostgreSQL schema.
- **dbt Transformation**: Modular dbt models for cleaning, type-casting, and dimensional modeling.
- **Star Schema**: Optimized database design for analytical queries.
- **Data Quality**: 15+ automated schema and data tests.

---

## 📂 Project Structure

```text
├── api/                # FastAPI Analytical API (Future Work)
├── data/
│   └── raw/            # Raw Data Lake
│       ├── images/     # Organized by channel
│       └── telegram_messages/ # Partitioned by YYYY-MM-DD
├── medical_warehouse/  # dbt Project
│   ├── models/
│   │   ├── staging/    # Data cleaning & type casting
│   │   └── marts/      # Star Schema (Dimensions & Facts)
│   └── tests/          # Custom dbt data tests
├── scripts/            # Diagnostic and utility scripts
├── src/                # Core pipeline scripts (Scraper, Loader)
├── logs/               # Processing logs
├── docker-compose.yml  # PostgreSQL & API Infrastructure
└── .env                # Secret management
```

---

## 🛠️ Setup & Installation

### 1. Requirements
- Python 3.10+
- Docker & Docker Desktop
- Telegram API Credentials ([my.telegram.org](https://my.telegram.org))

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
# Telegram API
TG_API_ID=your_id
TG_API_HASH=your_hash

# Database
DB_HOST=localhost
DB_PORT=5433
DB_NAME=medical_db
DB_USER=sa
DB_PASS=123
```

### 3. Start the Infrastructure
```bash
docker-compose up -d
```

---

## 🏗️ Pipeline Workflows

### Task 1: Data Scraping (Extract)
Extracts messages and images from specified Telegram channels.
```bash
python src/scraper.py
```
*Note: Authenticate with your phone number on the first run.*

### Task 2: Transformation (Load & Transform)
1. **Load Raw Data to Postgres**:
   ```bash
   python src/load_data.py
   ```
2. **Run dbt Transformations**:
   ```bash
   cd medical_warehouse
   dbt deps
   dbt run
   dbt test
   ```

---

## 📊 Data Model (Star Schema)

### Dimension Tables
- **`dim_channels`**: Metadata for scraped channels (CheMed123, Lobelia, etc.).
- **`dim_dates`**: Comprehensive date dimension for time-series analysis.

### Fact Table
- **`fct_messages`**: Centralized fact table linking messages to channels and dates with metrics like `view_count` and `forward_count`.

---

## ✅ Quality Assurance
- Automated schema tests for primary keys, nulls, and relationships.
- Custom Business Rule Tests (e.g., `assert_no_future_messages.sql`).
- Detailed processing logs in `logs/`.

---

## 📝 License
This project is developed for educational and experimental purposes.
