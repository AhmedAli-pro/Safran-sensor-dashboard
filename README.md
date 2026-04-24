# 🏭 Safran Industrial Sensor Dashboard

A Python-only web platform for industrial sensor data formalization and visualization, inspired by Microsoft Power BI functionalities. Built as part of a final-year internship project for **Safran Composites** (M&P Division).

> **Live project**: [github.com/AhmedAli-pro/Safran-sensor-dashboard](https://github.com/AhmedAli-pro/Safran-sensor-dashboard)

---

## 📌 Project Overview

Safran Composites is deploying new measurement sensors across its manufacturing equipment. This platform ingests raw sensor CSV files, runs a data formalization pipeline, stores the results, and exposes them through an interactive dashboard — all without requiring any BI license or non-Python tooling.

The dataset used is the **AI4I 2020 Predictive Maintenance Dataset** (UCI Machine Learning Repository), which simulates real industrial sensor readings including temperature, rotational speed, torque, and tool wear.

---

## 🏗️ Architecture

```
Raw CSV Upload (Streamlit)
        ↓
Schema Validation (FastAPI)
        ↓
Formalization Pipeline (Pandas)
  - Kelvin → Celsius conversion
  - Outlier detection (IQR method)
  - Equipment health score (0–100%)
  - Eco-design KPIs (energy + CO₂)
        ↓
SQLite Storage
        ↓
REST API (FastAPI)
  - GET /sensors
  - GET /kpis
  - GET /alerts
        ↓
Interactive Dashboard (Streamlit)
  - Sensor Trends tab
  - Correlation Heatmap tab
  - Eco-Design KPI tab
```

---

## 📁 Project Structure

```
Safran-sensor-dashboard/
│
├── app/
│   └── main.py               ← FastAPI backend (upload, sensors, kpis, alerts)
│
├── pipeline/
│   ├── __init__.py
│   ├── ingest.py             ← load raw CSV
│   └── formalize.py          ← formalization pipeline
│
├── frontend/
│   └── streamlit_app.py      ← Streamlit dashboard
│
├── data/
│   ├── raw/
│   │   └── sample.csv        ← AI4I 2020 dataset (download script below)
│   └── processed/
│       └── cleaned.db        ← auto-generated SQLite database
│
├── scripts/
│   └── download_data.py      ← one-time dataset download script
│
└── requirements.txt
```

---

## ⚙️ Features

### Data Formalization Pipeline
- **Unit conversion** — Kelvin to Celsius for temperature sensors
- **Outlier detection** — IQR method applied per sensor (rotational speed, torque, tool wear)
- **Equipment health score** — composite 0–100% metric derived from tool wear and torque
- **Schema validation** — rejects files with missing or incorrect columns with a clear error message

### REST API (FastAPI)
| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | API health check |
| `/upload` | POST | Upload and formalize CSV |
| `/sensors` | GET | Paginated sensor data with failure filter |
| `/kpis` | GET | Aggregated KPI metrics |
| `/alerts` | GET | Dynamic threshold-based alert system |

Interactive API docs available at `http://127.0.0.1:8000/docs` (Swagger UI).

### Dashboard (Streamlit)
- **KPI cards** — health score, failures, CO₂, tool wear, outliers
- **Sensor Trends** — time-series with machine failure event markers
- **Correlation Heatmap** — identifies sensor interdependencies
- **Eco-Design tab** — energy consumption (kWh) and CO₂ emissions (kg) per cycle

### Eco-Design KPIs
CO₂ estimation using the official **ADEME French grid emission factor (0.233 kg CO₂/kWh)**:

```
Power (W)    = Torque (Nm) × ω (rad/s) = Torque × (RPM × 2π / 60)
Energy (kWh) = Power / 3,600,000
CO₂ (kg)     = Energy × 0.233
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/AhmedAli-pro/Safran-sensor-dashboard.git
cd Safran-sensor-dashboard
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the dataset
```bash
python scripts/download_data.py
```

### 5. Run the FastAPI backend
```bash
uvicorn app.main:app --reload
```

### 6. Run the Streamlit frontend (new terminal)
```bash
streamlit run frontend/streamlit_app.py
```

### 7. Open the dashboard
Go to `http://localhost:8501`, upload `data/raw/sample.csv` and explore the dashboard.

---

## 📊 Dataset

**AI4I 2020 Predictive Maintenance Dataset**
- Source: [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)
- 10,000 rows, 14 columns
- Sensors: Air temperature, Process temperature, Rotational speed, Torque, Tool wear
- Target: Machine failure (binary) with failure mode breakdown (TWF, HDF, PWF, OSF, RNF)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Frontend | Streamlit |
| Data processing | Pandas, NumPy |
| Visualization | Plotly |
| Database | SQLite |
| Language | Python 3.x |

---

## 👤 Author

**Ahmed Ali**
M2 Big Data & Business Analytics — CY Cergy Paris Université (CY Tech)

[LinkedIn](https://www.linkedin.com/in/ahmed-ali-a31826231/) · [GitHub](https://github.com/AhmedAli-pro)
