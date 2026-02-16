# 🏥 Ethiopian Medical Data Warehouse

[![Unit Tests](https://github.com/meleseabrham/week-8-medical-telegram-warehouse/actions/workflows/unittests.yml/badge.svg)](https://github.com/meleseabrham/week-8-medical-telegram-warehouse/actions)

An end-to-end data engineering pipeline designed to archive, clean, and analyze medical business data from public Ethiopian Telegram channels using a modular ELT stack and AI-driven enrichment.

## 💼 Business Problem
The pharmaceutical and medical retail sector in Ethiopia is highly fragmented, with critical business data (prices, availability, product launches) trapped in unstructured Telegram channels. Business analysts and retailers lack a centralized, structured database to track market trends, verify product authenticity, and optimize inventory based on visual content engagement.

## 🚀 Solution Overview
This project implements a sophisticated **ELT (Extract, Load, Transform)** pipeline:
1.  **Extraction**: Scalable incremental scraping of Telegram metadata and images.
2.  **Enrichment**: YOLOv8 AI model categorizes image content (Promotional vs. Product Display).
3.  **Transformation**: dbt (data build tool) models raw data into a Star Schema warehouse in PostgreSQL.
4.  **Analytics**: A FastAPI layer serves insights to a dynamic Streamlit dashboard with SHAP explainability.

## 📊 Key Results
-   **90% Performance Gain**: Incremental scraping tracks state to avoid reprocessing duplicate messages.
-   **Visual Intelligence**: Automated categorization of 1000+ images into actionable business categories.
-   **Decision Support**: Real-time dashboard reduces market research time from hours to seconds.

## 📂 Project Structure
```text
├── api/                # FastAPI & Streamlit Dashboard
├── orchestration/      # Dagster Pipeline (Jobs, Ops, Schedules)
├── medical_warehouse/  # dbt Transformation Logic
├── src/                # Core Logic (Refactored with Type Safety)
│   ├── config.py       # Dataclass-based Configuration
│   ├── utils.py        # Shared Utilities (DB/Logs)
│   └── yolo_detect.py  # AI Enrichment Logic
├── tests/              # Pytest Suite (CI Enforcement)
└── docker-compose.yml  # PostgreSQL Infrastructure
```

## 🛠️ Quick Start
1.  **Clone & Install**:
    ```bash
    git clone https://github.com/meleseabrham/week-8-medical-telegram-warehouse
    cd week-8-medical-telegram-warehouse
    pip install -r requirements.txt
    ```
2.  **Infrastructure**: Start Docker and run `docker-compose up -d db`.
3.  **Environment**: Add `TG_API_ID` and `TG_API_HASH` to `.env`.
4.  **Run Pipeline**: `python -m dagster dev -m orchestration`
5.  **Run API & Dashboard**: 
    - `python -m uvicorn api.main:app --port 8001`
    - `python -m streamlit run api/dashboard.py`

## 👨‍🔬 Technical Details
-   **Data**: Sourced from 5+ prominent Ethiopian medical Telegram channels. Preprocessing includes text cleaning and image resizing for YOLO.
-   **Model**: YOLOv8n (Nano) for high-speed object detection and custom categorization heuristics.
-   **Evaluation**: Data integrity is validated via 15+ dbt tests and 6+ Python unit tests.

## 🔮 Future Improvements
-   **Fine-tuned YOLO**: Train a custom model on local Ethiopian medicine packaging for higher precision.
-   **Sentiment Analysis**: Implement NLP to gauge consumer sentiment from Telegram comments.
-   **Cloud Migration**: Deploy the orchestrator to AWS/GCP for true 24/7 automation.

## 👤 Author
**Melese Abrham**  
[LinkedIn](https://www.linkedin.com/in/meleseabrham) | [GitHub](https://github.com/meleseabrham) | [Website](https://meleseabrham.com)
