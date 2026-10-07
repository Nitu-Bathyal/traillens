import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.tabpfn_predictor import tabpfn_service
from app.models.prediction import ActivityPredictionRequest


def test_tabpfn_service_initialization():
    assert tabpfn_service.model_name
    assert "cv_accuracy_mean" in tabpfn_service.benchmark_metrics
    assert tabpfn_service.benchmark_metrics["cv_accuracy_mean"] > 0.5
    assert len(tabpfn_service.benchmark_metrics["classes"]) > 0


@pytest.mark.asyncio
async def test_predict_activity_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "temperature_c": 21.0,
            "humidity_pct": 52.0,
            "cloud_cover_pct": 25.0,
            "time_of_day": "morning",
            "day_of_week": "weekend",
            "available_minutes": 30,
            "terrain": "park",
            "user_energy": "moderate"
        }
        res = await client.post("/api/predict-activity", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "recommended_activity" in data
        assert "completion_likelihood_pct" in data
        assert data["completion_likelihood_pct"] >= 0.0
        assert "evaluation_metrics" in data
        assert "limitations" in data
        assert data["suggested_duration_min"] <= 30
