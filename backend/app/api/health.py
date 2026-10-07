from datetime import datetime, timezone
from fastapi import APIRouter
from app.config import settings
from app.services.db import db_service
from app.ai.factory import get_ai_provider
from app.services.tabpfn_predictor import tabpfn_service

router = APIRouter(tags=["Health & Status"])


@router.get("/health")
async def health_check():
    provider = get_ai_provider()
    db_status = db_service.get_status()

    return {
        "status": "healthy",
        "service": "TrailLens Outdoor Companion API",
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ai_provider": {
            "name": provider.name,
            "model": provider.model_name,
            "license": provider.license,
            "is_offline": provider.is_offline
        },
        "database": db_status,
        "tabular_predictor": {
            "model_name": tabpfn_service.model_name,
            "tabpfn_native": tabpfn_service.tabpfn_available,
            "benchmark_accuracy": tabpfn_service.benchmark_metrics.get("cv_accuracy_mean")
        },
        "observability": {
            "sentry_configured": bool(settings.SENTRY_DSN)
        },
        "voice_narration": {
            "elevenlabs_configured": bool(settings.ELEVENLABS_API_KEY)
        }
    }
