import time
import io
import base64
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from pydantic import BaseModel, Field
from PIL import Image

from app.config import settings
from app.ai.factory import get_ai_provider
from app.models.observation import IdentificationResult
from app.services.sentry_service import capture_inference_metric

router = APIRouter(prefix="/api", tags=["Identification"])


class IdentifyJsonRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded image string")
    user_hint: Optional[str] = Field(None, description="Optional user context or observation note")


def validate_image_bytes(content: bytes) -> Image.Image:
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image exceeds maximum permitted size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    try:
        image = Image.open(io.BytesIO(content))
        image.verify()  # Verify image integrity
        # Re-open after verify() because verify() clears file pointer
        image = Image.open(io.BytesIO(content))
        image.load()
        return image
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Supported formats: JPEG, PNG, WebP."
        )


@router.post("/identify", response_model=IdentificationResult)
async def identify_nature_upload(
    file: UploadFile = File(...),
    user_hint: Optional[str] = Form(None)
):
    """
    Primary nature identification endpoint via multipart image upload.
    Processes nature photograph using configured open-weight model or demo engine.
    """
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported media type '{file.content_type}'. Allowed types: {settings.ALLOWED_IMAGE_TYPES}"
        )

    content = await file.read()
    image = validate_image_bytes(content)

    provider = get_ai_provider()
    start_time = time.time()
    try:
        result = await provider.identify(image, user_hint)
        latency_ms = (time.time() - start_time) * 1000
        capture_inference_metric(latency_ms, provider.model_name, success=True)
        return result
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        capture_inference_metric(latency_ms, provider.model_name, success=False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error with model {provider.model_name}: {str(e)}"
        )


@router.post("/identify-json", response_model=IdentificationResult)
async def identify_nature_json(payload: IdentifyJsonRequest):
    """
    Base64 JSON alternative for offline-first web clients and service worker background sync.
    """
    raw_b64 = payload.image_base64
    if "," in raw_b64:
        raw_b64 = raw_b64.split(",", 1)[1]

    try:
        content = base64.b64decode(raw_b64)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed base64 image data."
        )

    image = validate_image_bytes(content)
    provider = get_ai_provider()
    start_time = time.time()
    try:
        result = await provider.identify(image, payload.user_hint)
        latency_ms = (time.time() - start_time) * 1000
        capture_inference_metric(latency_ms, provider.model_name, success=True)
        return result
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        capture_inference_metric(latency_ms, provider.model_name, success=False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {str(e)}"
        )
