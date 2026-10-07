from fastapi import APIRouter
from app.models.prediction import ActivityPredictionRequest, ActivityPredictionResponse
from app.services.tabpfn_predictor import tabpfn_service

router = APIRouter(prefix="/api", tags=["Tabular Nature Predictor"])


@router.post("/predict-activity", response_model=ActivityPredictionResponse)
async def predict_outdoor_activity(req: ActivityPredictionRequest):
    """
    Predicts optimal outdoor engagement category and likelihood of completing
    a screen-free observation based on tabular ambient conditions using TabPFN / Tabular model.
    """
    return tabpfn_service.predict(req)
