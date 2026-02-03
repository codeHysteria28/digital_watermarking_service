from fastapi import FastAPI
from datetime import datetime
from routes.user_route import router as users_router
from models.user import Base
from core.database import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digital Watermarking Service Backend",
    description="Backend service for managing users and digital watermarking operations.",
    version="1.0.0"
)
app.include_router(users_router)

@app.get("/health", status_code=200)
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now()
    }