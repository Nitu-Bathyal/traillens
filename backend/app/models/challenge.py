from typing import Optional
from pydantic import BaseModel, Field


class Challenge(BaseModel):
    id: str
    title: str
    category: str = Field("mindfulness", description="botany, mindfulness, acoustics, textures, weather, insects")
    duration_minutes: int = Field(3, ge=1, le=60)
    instruction: str
    screen_rule: str = Field("Turn your phone face down or slip it in your pocket.", description="Rule to disengage device")
    difficulty: str = Field("easy", description="easy, moderate")
    equipment_needed: str = Field("None — just eyes and ears", description="Required gear")
    follow_up_prompt: Optional[str] = Field(None, description="Optional reflection question after putting phone away")
