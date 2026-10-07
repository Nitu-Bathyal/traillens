from typing import Dict, Any
from pydantic import BaseModel, Field


class ActivityPredictionRequest(BaseModel):
    temperature_c: float = Field(20.0, description="Ambient temperature in Celsius")
    humidity_pct: float = Field(55.0, ge=0.0, le=100.0, description="Humidity percentage")
    cloud_cover_pct: float = Field(30.0, ge=0.0, le=100.0, description="Cloud cover percentage (0-100)")
    time_of_day: str = Field("morning", description="morning, afternoon, evening, twilight")
    day_of_week: str = Field("weekend", description="weekday, weekend")
    available_minutes: int = Field(20, ge=5, le=180, description="Available outdoor time in minutes")
    terrain: str = Field("park", description="park, forest_trail, coastal, urban_green, backyard")
    user_energy: str = Field("moderate", description="gentle, moderate, active")


class ActivityPredictionResponse(BaseModel):
    recommended_activity: str
    category: str
    confidence_score: float
    completion_likelihood_pct: float
    suggested_duration_min: int
    rationale: str
    features_used: Dict[str, Any]
    model_name: str
    evaluation_metrics: Dict[str, Any]
    limitations: str
