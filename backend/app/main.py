"""FastAPI application entry point."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.runtime.context import AnalyticsRuntimeState, initialize_runtime


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.analytics_runtime = initialize_runtime()
    try:
        yield
    finally:
        application.state.analytics_runtime = AnalyticsRuntimeState("not_configured")


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
        lifespan=lifespan,
    )
    application.state.analytics_runtime = AnalyticsRuntimeState("not_configured")

    @application.middleware("http")
    async def assessment_cache_policy(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/v1/assessments/"):
            response.headers["Cache-Control"] = "no-store"
        return response

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
