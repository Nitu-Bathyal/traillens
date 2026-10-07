from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from app.models.challenge import Challenge
from app.services.challenges import challenge_service

router = APIRouter(prefix="/api/challenges", tags=["Outdoor Challenges"])


@router.get("/random", response_model=Challenge)
async def get_random_challenge(category: Optional[str] = None):
    """
    Get a randomly selected outdoor observation challenge designed to get
    the explorer off screens and tuned into real-world nature phenomena.
    """
    return challenge_service.get_random(category=category)


@router.get("", response_model=List[Challenge])
async def list_challenges():
    """
    List all cataloged outdoor challenges.
    """
    return challenge_service.get_all()


@router.get("/{challenge_id}", response_model=Challenge)
async def get_challenge_by_id(challenge_id: str):
    c = challenge_service.get_by_id(challenge_id)
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge '{challenge_id}' not found."
        )
    return c
