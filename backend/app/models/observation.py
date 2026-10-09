from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class IdentificationResult(BaseModel):
    identification: str = Field(..., description="Likely common name")
    scientific_name: Optional[str] = Field(None, description="Scientific binomial name if known")
    category: str = Field("flora", description="Category: flora, fauna, fungi, geology, weather")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    confidence_level: str = Field("moderate", description="high, moderate, or uncertain")
    summary: str = Field(..., description="Concise explanation of the organism or nature element")
    observations: List[str] = Field(default_factory=list, description="Key real-world details to observe")
    outdoor_challenge: str = Field(..., description="Actionable outdoor challenge requiring zero screen time")
    safety_note: str = Field(
        "Never consume or handle wild plants, mushrooms, or wildlife based on digital identification.",
        description="Important real-world safety warning"
    )
    screen_break_message: str = Field(
        "Put your phone away and spend 3 minutes observing this organism in its natural habitat.",
        description="Explicit nudge to step away from the screen"
    )
    model_used: str = Field("gemma-2-2b-open-weights", description="Model name and weights used")
    is_demo: bool = Field(False, description="Whether this response was synthesized in demo mode")
    is_confident: bool = Field(True, description="False if no organism can be confidently identified")
    fallback_warning: Optional[str] = Field(
        None,
        description="Explicit notice when running in illustrative fallback or demo mode without a live vision model"
    )
    scene_description: Optional[str] = Field(
        None,
        description="Objective description of visual landscape or image characteristics"
    )


class ObservationCreate(BaseModel):
    session_id: Optional[str] = Field("anon-explorer", description="Anonymous user/session ID")
    identification: IdentificationResult
    latitude: Optional[float] = Field(None, description="Approximate latitude if user opted-in")
    longitude: Optional[float] = Field(None, description="Approximate longitude if user opted-in")
    user_notes: Optional[str] = Field(None, description="Optional notes written by explorer after challenge")
    image_thumbnail: Optional[str] = Field(None, description="Lightweight thumbnail base64 if kept locally")
    offline_created_at: Optional[str] = Field(None, description="ISO timestamp recorded while offline")
    client_id: Optional[str] = Field(None, description="Unique client-generated ID for offline reconciliation")


class Observation(BaseModel):
    id: str = Field(..., description="Database identifier")
    session_id: str
    identification: IdentificationResult
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    user_notes: Optional[str] = None
    image_thumbnail: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sync_status: str = Field("synced", description="synced or pending")
    client_id: Optional[str] = None


class SyncBatchRequest(BaseModel):
    observations: List[ObservationCreate]


class SyncBatchResponse(BaseModel):
    synced_count: int
    items: List[Observation]
