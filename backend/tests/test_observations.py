import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_observation_crud_and_sync():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create observation
        sample_obs = {
            "session_id": "test-explorer-101",
            "identification": {
                "identification": "Common Dandelion",
                "scientific_name": "Taraxacum officinale",
                "category": "flora",
                "confidence": 0.88,
                "confidence_level": "high",
                "summary": "Yellow composite flower.",
                "observations": ["Check leaf lobes"],
                "outdoor_challenge": "Spend 3 minutes observing without screens.",
                "safety_note": "Do not ingest.",
                "screen_break_message": "Put your phone away.",
                "model_used": "Test-Model",
                "is_demo": True
            },
            "latitude": 51.5074,
            "longitude": -0.1278,
            "user_notes": "Noticed 14 jagged lobes on leaf edge."
        }

        create_res = await client.post("/api/observations", json=sample_obs)
        assert create_res.status_code == 201
        created_data = create_res.json()
        obs_id = created_data["id"]
        assert obs_id is not None
        assert created_data["session_id"] == "test-explorer-101"

        # 2. List observations
        list_res = await client.get("/api/observations?session_id=test-explorer-101")
        assert list_res.status_code == 200
        items = list_res.json()
        assert len(items) >= 1
        assert any(i["id"] == obs_id for i in items)

        # 3. Test offline batch sync
        sync_payload = {
            "observations": [
                {
                    "session_id": "test-explorer-101",
                    "client_id": "client-uuid-offline-1",
                    "offline_created_at": "2026-10-07T08:00:00Z",
                    "identification": sample_obs["identification"],
                    "user_notes": "Captured while offline on the woodland trail."
                }
            ]
        }
        sync_res = await client.post("/api/observations/sync", json=sync_payload)
        assert sync_res.status_code == 200
        sync_data = sync_res.json()
        assert sync_data["synced_count"] == 1
        assert len(sync_data["items"]) == 1

        # 4. Delete observation
        del_res = await client.delete(f"/api/observations/{obs_id}")
        assert del_res.status_code == 200
        assert del_res.json()["status"] == "deleted"
