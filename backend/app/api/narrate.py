from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.narration import narration_service

router = APIRouter(prefix="/api", tags=["Voice Narration"])


class NarrateRequest(BaseModel):
    identification: str = Field(..., description="Species or element identification")
    observation_hint: str = Field(..., description="Key detail to observe")
    challenge_duration: int = Field(3, description="Minutes to spend outdoors")
    custom_text: Optional[str] = Field(None, description="Direct text to narrate if provided")


@router.post("/narrate")
async def narrate_nature_cue(payload: NarrateRequest):
    """
    Generates a spoken audio cue or client speech payload.
    Briefly highlights what to look for and explicitly instructs the user
    to lock their screen and observe in real life.
    """
    if payload.custom_text:
        script = payload.custom_text
    else:
        script = narration_service.prepare_script(
            identification=payload.identification,
            observation_hint=payload.observation_hint,
            challenge_duration=payload.challenge_duration
        )

    return await narration_service.generate_speech(script)
