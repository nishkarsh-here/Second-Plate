"""FastAPI application entrypoint.

Wires CORS, routers (under the configured API prefix), a consistent error shape
for domain errors, and loads the trained model into cache at startup.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import AppError
from app.ml import model_store
from app.routers import impact, listings, meta, ml, predictions
from app.schemas.common import HealthResponse

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("secondplate")

OPENAPI_TAGS = [
    {"name": "listings", "description": "Post, browse, claim and inspect surplus food listings."},
    {"name": "impact", "description": "Aggregated rescue impact: meals, kg saved, CO2e, people served."},
    {"name": "predictions", "description": "Per-donor next-day surplus forecasts with explainability."},
    {"name": "ml", "description": "Model lifecycle (retrain + metrics)."},
    {"name": "reference", "description": "Donors and recipients reference data."},
    {"name": "meta", "description": "Health and service metadata."},
]

DESCRIPTION = (
    "Backend for **SecondPlate**, a surplus-food rescue platform that connects "
    "food donors with recipients, scores listing freshness-urgency, aggregates "
    "rescue impact, and forecasts each donor's next-day surplus with a "
    "GradientBoostingRegressor."
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        if model_store.is_loaded():
            logger.info("Surplus model loaded from %s", model_store.MODEL_PATH)
        else:
            logger.warning("No trained model found — call POST %s/ml/retrain", settings.api_prefix)
    except Exception as exc:  # pragma: no cover - never block startup on the model
        logger.warning("Model load skipped: %s", exc)
    yield


app = FastAPI(
    title=f"{settings.app_name} API",
    description=DESCRIPTION,
    version="1.0.0",
    openapi_tags=OPENAPI_TAGS,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    # jsonable_encoder makes the error context (which may hold a ValueError) safe.
    return JSONResponse(status_code=422, content=jsonable_encoder({"detail": exc.errors()}))


for router in (meta.router, listings.router, impact.router, predictions.router, ml.router):
    app.include_router(router, prefix=settings.api_prefix)


@app.get("/health", response_model=HealthResponse, tags=["meta"], summary="Service health")
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        environment=settings.environment,
        database="sqlite" if settings.is_sqlite else "postgresql",
        model_loaded=model_store.is_loaded(),
    )


@app.get("/", tags=["meta"], summary="Service root")
def root() -> dict:
    return {"name": f"{settings.app_name} API", "docs": "/docs", "health": "/health"}
