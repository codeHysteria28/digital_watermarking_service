from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health", status_code=200)
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now()
    }