from fastapi import FastAPI
from datetime import datetime
from app.routes.user_route import router as users_router
from app.routes.image_route import router as images_router
from app.routes.verification_route import router as verification_router
from app.models.base import Base
from app.core.database import engine
from fastapi.middleware.cors import CORSMiddleware
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digital Watermarking Service Backend",
    description="Backend service for managing users and digital watermarking operations.",
    version="1.0.0"
)

# CORS Issues, sicne frontend and backend will be deployed on different URLs we need to setup CORS origin allowlist
# By default it will use wildcard CORS if nothing is specified in the ALLOWED_ORIGINS env variable.
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,  # must be False when using wildcard origin
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(images_router)
app.include_router(verification_router)

@app.get("/health", status_code=200)
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now()
    }
