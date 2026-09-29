# app/main.py
from fastapi import FastAPI

app = FastAPI(title="NetOps Agent")

@app.get("/health")
def health():
    return {"status": "ok"}