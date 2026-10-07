from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.identify import router as identify_router
from app.api.observations import router as observations_router
from app.api.challenges import router as challenges_router
from app.api.predict import router as predict_router
from app.api.narrate import router as narrate_router
from app.api.providers import router as providers_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(identify_router)
api_router.include_router(observations_router)
api_router.include_router(challenges_router)
api_router.include_router(predict_router)
api_router.include_router(narrate_router)
api_router.include_router(providers_router)
