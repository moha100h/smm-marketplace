"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SMM Marketplace API",
    description="Enterprise Telegram Virtual Services Marketplace",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
async def startup():
    logger.info("SMM Marketplace API started")


@app.on_event("shutdown")
async def shutdown():
    logger.info("SMM Marketplace API shutting down")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/")
async def root():
    return {
        "message": "SMM Marketplace API",
        "docs": "/docs",
        "health": "/health",
    }
