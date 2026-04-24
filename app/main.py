from fastapi import FastAPI, UploadFile
import pandas as pd
import sqlite3
import os
from pipeline.formalize import formalize

app = FastAPI()

os.makedirs("data/processed", exist_ok=True)

@app.get("/")
def root():
    return {"status": "Safran Sensor API is running"}

@app.post("/upload")
async def upload(file: UploadFile):
    df = pd.read_csv(file.file)

    required = [
    "Air temperature", "Process temperature",
    "Rotational speed", "Torque", "Tool wear"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return {"error": f"Missing columns: {missing}"}

    df_clean = formalize(df)

    conn = sqlite3.connect("data/processed/cleaned.db")
    df_clean.to_sql("sensor_data", conn, if_exists="replace", index=False)
    conn.close()

    return {
        "status": "ok",
        "rows": len(df_clean),
        "columns": list(df_clean.columns),
        "preview": df_clean.head(5).to_dict(orient="records")
    }


@app.get("/sensors")
def get_sensors(limit: int = 500, failure_only: bool = False):
    if not os.path.exists("data/processed/cleaned.db"):
        return []
    conn = sqlite3.connect("data/processed/cleaned.db")
    df = pd.read_sql("SELECT * FROM sensor_data", conn)
    conn.close()
    if failure_only:
        df = df[df["machine_failure"] == 1]
    return df.tail(limit).to_dict(orient="records")


@app.get("/kpis")
def get_kpis():
    if not os.path.exists("data/processed/cleaned.db"):
        return {"error": "no_data"}
    conn = sqlite3.connect("data/processed/cleaned.db")
    df = pd.read_sql("SELECT * FROM sensor_data", conn)
    conn.close()
    return {
        "avg_health_score":  round(df["health_score"].mean(), 1),
        "total_failures":    int(df["machine_failure"].sum()),
        "total_co2_kg":      round(df["co2_kg"].sum(), 2),
        "avg_tool_wear_min": round(df["tool_wear_min"].mean(), 1),
        "outlier_count": int(df["rot_speed_rpm_outlier"].sum()),
    }


@app.get("/alerts")
def get_alerts(torque_max: float = 60.0, wear_max: float = 200.0):
    if not os.path.exists("data/processed/cleaned.db"):
        return {"alert_count": 0, "records": []}
    conn = sqlite3.connect("data/processed/cleaned.db")
    df = pd.read_sql("SELECT * FROM sensor_data", conn)
    conn.close()
    alerts = df[
        (df["torque_nm"] > torque_max) |
        (df["tool_wear_min"] > wear_max)
    ]
    return {"alert_count": len(alerts), "records": alerts.head(50).to_dict(orient="records")}
