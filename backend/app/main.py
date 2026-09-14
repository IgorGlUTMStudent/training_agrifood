"""FastAPI application entry point."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


def _cors_origins() -> list[str]:
    configured = os.getenv(
        "SMART_HARVEST_CORS_ORIGINS", "http://localhost:5173"
    )
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


def create_app() -> FastAPI:
    application = FastAPI(
        title="Smart Harvest API",
        version="0.1.0",
        description="Foundation API for a simulation/training challenge.",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    application.include_router(router, prefix="/api/v1")
    return application


app = create_app()
