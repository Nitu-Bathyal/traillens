from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from app.models.observation import Observation, ObservationCreate, SyncBatchRequest, SyncBatchResponse
from app.services.db import db_service

router = APIRouter(prefix="/api/observations", tags=["Observations"])


@router.get("", response_model=List[Observation])
async def list_observations(
    session_id: Optional[str] = None,
    limit: int = 50
):
    """
    Retrieve stored nature observations.
    Works seamlessly with MongoDB Atlas or the local SQLite storage layer.
    """
    return await db_service.get_observations(session_id=session_id, limit=limit)


@router.post("", response_model=Observation, status_code=status.HTTP_201_CREATED)
async def create_observation(obs_in: ObservationCreate):
    """
    Save a new field observation after completing or noting an outdoor challenge.
    """
    return await db_service.insert_observation(obs_in)


@router.delete("/{obs_id}")
async def delete_observation(obs_id: str):
    """
    Delete a specific observation to honor user privacy and data ownership.
    """
    success = await db_service.delete_observation(obs_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Observation with ID '{obs_id}' not found."
        )
    return {"status": "deleted", "id": obs_id}


@router.post("/sync", response_model=SyncBatchResponse)
async def sync_offline_observations(batch: SyncBatchRequest):
    """
    Batch sync endpoint for offline-queued observations captured on trails
    when connectivity is restored.
    """
    synced_items = await db_service.sync_batch(batch.observations)
    return SyncBatchResponse(
        synced_count=len(synced_items),
        items=synced_items
    )
