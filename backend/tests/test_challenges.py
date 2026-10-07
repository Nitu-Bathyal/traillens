import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.challenges import challenge_service
from app.services.narration import narration_service


def test_challenges_service():
    challenges = challenge_service.get_all()
    assert len(challenges) >= 5

    rand = challenge_service.get_random()
    assert rand.title
    assert rand.duration_minutes > 0
    assert rand.screen_rule


@pytest.mark.asyncio
async def test_challenges_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/challenges/random")
        assert res.status_code == 200
        data = res.json()
        assert "instruction" in data
        assert "screen_rule" in data


def test_narration_script_generation():
    script = narration_service.prepare_script(
        identification="Common Dandelion",
        observation_hint="yellow florets and stem latex",
        challenge_duration=3
    )
    assert "Common Dandelion" in script
    assert "put your phone away" in script.lower()
