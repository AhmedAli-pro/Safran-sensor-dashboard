import pandas as pd
import numpy as np

def formalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
    "Air temperature":    "air_temp_k",   # store raw as Kelvin
    "Process temperature": "proc_temp_k",
    "Rotational speed":   "rot_speed_rpm",
    "Torque":             "torque_nm",
    "Tool wear":          "tool_wear_min",
    "Machine failure":    "machine_failure",
    })
    # Convert to Celsius for display
    df["air_temp_c"]  = (df["air_temp_k"]  - 273.15).round(2)
    df["proc_temp_c"] = (df["proc_temp_k"] - 273.15).round(2)
    # Outlier flagging — IQR method on 3 sensors with real variance
    for col in ["rot_speed_rpm", "torque_nm", "tool_wear_min"]:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        df[f"{col}_outlier"] = ~df[col].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)

    # Equipment health score (0–100%)
    wear_norm   = 1 - (df["tool_wear_min"] / df["tool_wear_min"].max())
    torque_norm = 1 - (df["torque_nm"]     / df["torque_nm"].max())
    df["health_score"] = ((wear_norm + torque_norm) / 2 * 100).round(1)

    # Eco-design KPIs
    df["energy_kwh"] = (df["torque_nm"] * df["rot_speed_rpm"] * 2 * np.pi / 60 / 3600).round(4)
    df["co2_kg"]     = (df["energy_kwh"] * 0.233).round(4)

    return df