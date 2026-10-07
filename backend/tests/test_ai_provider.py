import pytest
from PIL import Image
from app.ai.demo_provider import DemoAIProvider
from app.ai.open_model_provider import OpenModelProvider
from app.ai.factory import get_ai_provider


@pytest.mark.asyncio
async def test_demo_ai_provider():
    provider = DemoAIProvider()
    assert provider.name == "demo"
    assert provider.is_offline is True
    assert "Apache 2.0" in provider.license

    # Create dummy 100x100 RGB image
    img = Image.new("RGB", (100, 100), color=(34, 139, 34))
    result = await provider.identify(img)

    assert result.identification
    assert result.confidence > 0.0
    assert result.summary
    assert len(result.observations) > 0
    assert result.outdoor_challenge
    assert result.is_demo is True
    assert "screen_break_message" in result.model_dump()


def test_open_model_provider_json_cleaning():
    provider = OpenModelProvider()
    dirty_json = """```json
    {
        "identification": "English Oak",
        "scientific_name": "Quercus robur",
        "category": "flora",
        "confidence": 0.85,
        "confidence_level": "high",
        "summary": "Deciduous tree.",
        "observations": ["Look at lobed leaves"],
        "outdoor_challenge": "Observe canopy for 3 minutes.",
        "safety_note": "Do not consume raw acorns.",
        "screen_break_message": "Put phone away."
    }
    ```"""
    parsed = provider._clean_json_response(dirty_json)
    assert parsed["identification"] == "English Oak"
    assert parsed["confidence"] == 0.85


def test_ai_factory_default():
    provider = get_ai_provider()
    assert provider is not None
    assert hasattr(provider, "identify")
