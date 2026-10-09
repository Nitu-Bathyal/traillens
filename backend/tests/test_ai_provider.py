import pytest
from PIL import Image, ImageDraw
from app.ai.demo_provider import DemoAIProvider
from app.ai.open_model_provider import OpenModelProvider
from app.ai.factory import get_ai_provider
from app.ai.image_analyzer import extract_visual_metrics, analyze_image_heuristics


@pytest.mark.asyncio
async def test_demo_ai_provider():
    provider = DemoAIProvider()
    assert provider.name == "demo"
    assert provider.is_offline is True
    assert "Apache 2.0" in provider.license

    # Create dummy green foliage image
    img = Image.new("RGB", (100, 100), color=(34, 139, 34))
    result = await provider.identify(img)

    assert result.identification
    assert result.confidence > 0.0
    assert result.summary
    assert len(result.observations) > 0
    assert result.outdoor_challenge
    assert result.is_demo is True
    assert result.fallback_warning is not None
    assert "screen_break_message" in result.model_dump()


@pytest.mark.asyncio
async def test_sunset_landscape_no_species_fabrication():
    """
    Direct test for the user's issue: A sunset landscape containing trees and foliage
    must NOT return 'European Honeybee on Blossom' or fabricated high confidence.
    """
    sunset_img = Image.new("RGB", (120, 120))
    draw = ImageDraw.Draw(sunset_img)
    # Warm golden/red upper half (sunset sky)
    for y in range(60):
        draw.line([(0, y), (120, y)], fill=(255, int(100 + y * 1.5), 30))
    # Green/dark lower half (terrain and trees)
    for y in range(60, 120):
        draw.line([(0, y), (120, y)], fill=(34, int(90 + y * 0.4), 34))

    provider = DemoAIProvider()
    result = await provider.identify(sunset_img)

    # Must NOT claim high confidence or a specific animal species like Honeybee
    assert "Honeybee" not in result.identification
    assert "No confident identification" in result.identification
    assert result.confidence <= 0.20
    assert result.confidence_level == "uncertain"
    assert result.is_confident is False
    assert result.is_demo is True
    assert result.fallback_warning is not None
    assert "sunset" in result.summary.lower() or "landscape" in result.summary.lower()


@pytest.mark.asyncio
async def test_open_model_provider_fallback_labelling():
    """
    When OpenModelProvider cannot reach a live Ollama or Hugging Face endpoint,
    it must NOT label the result as Gemma/PaliGemma inference.
    """
    provider = OpenModelProvider(
        model_name="google/gemma-2-2b-it",
        vision_model_name="google/paligemma-3b-pt-224"
    )
    # Green foliage test image
    img = Image.new("RGB", (80, 80), color=(40, 140, 40))
    result = await provider.identify(img)

    # Must be marked as demo/fallback, with warning and honest model label
    assert result.is_demo is True
    assert result.fallback_warning is not None
    assert "LIVE INFERENCE UNAVAILABLE" in result.fallback_warning
    # Must NOT claim that Gemma/PaliGemma was the actual model that ran
    assert "Fallback" in result.model_used or "Offline" in result.model_used


@pytest.mark.asyncio
async def test_low_light_ambiguous_image():
    """
    A dark or underexposed image must return low confidence and an explicit notice.
    """
    dark_img = Image.new("RGB", (64, 64), color=(10, 10, 10))
    result = analyze_image_heuristics(dark_img)

    assert result.is_confident is False
    assert result.confidence <= 0.10
    assert result.confidence_level == "uncertain"
    assert "Low Light" in result.identification or "No confident" in result.identification


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
