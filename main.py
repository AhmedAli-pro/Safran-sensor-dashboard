from fastapi import FastAPI, UploadFile, File
import pandas as pd

app = FastAPI()

data = None

@app.get("/")
def home():
    return {"message": "API is running"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global data
    data = pd.read_csv(file.file)
    return {"message": "File uploaded successfully", "columns": list(data.columns)}

@app.get("/summary")
def summary():
    if data is None:
        return {"error": "No data uploaded"}
    return data.describe().to_dict()

@app.get("/columns")
def columns():
    if data is None:
        return {"error": "No data uploaded"}
    return {"columns": list(data.columns)}