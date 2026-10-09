import io
import pytest
from PIL import Image, ImageDraw
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_identify_multipart_endpoint():
    # Generate in-memory PNG (green foliage)
    img = Image.new("RGB", (64, 64), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("foliage.png", buf.getvalue(), "image/png")}
        data = {"user_hint": "Wild leaves"}
        response = await client.post("/api/identify", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert "identification" in result
        assert "outdoor_challenge" in result
        assert "screen_break_message" in result
        assert result["confidence"] > 0
        assert result["is_demo"] is True
        assert result["fallback_warning"] is not None


@pytest.mark.asyncio
async def test_identify_json_endpoint():
    import base64
    img = Image.new("RGB", (64, 64), color=(100, 200, 100))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "image_base64": f"data:image/jpeg;base64,{b64_str}",
            "user_hint": "Green leaf in shaded park"
        }
        response = await client.post("/api/identify-json", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "identification" in data
        assert data["category"] in ["flora", "fauna", "fungi", "geology", "weather"]


@pytest.mark.asyncio
async def test_identify_sunset_landscape_endpoint():
    """
    Ensure the API endpoint refuses to hallucinate species on a sunset photo.
    """
    sunset = Image.new("RGB", (100, 100))
    draw = ImageDraw.Draw(sunset)
    # Sunset gradient top
    for y in range(50):
        draw.line([(0, y), (100, y)], fill=(255, int(110 + y), 35))
    # Foliage gradient bottom
    for y in range(50, 100):
        draw.line([(0, y), (100, y)], fill=(34, int(100 + y * 0.3), 34))

    buf = io.BytesIO()
    sunset.save(buf, format="JPEG")
    buf.seek(0)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("sunset.jpg", buf.getvalue(), "image/jpeg")}
        res = await client.post("/api/identify", files=files)
        assert res.status_code == 200
        data = res.json()

        assert "Honeybee" not in data["identification"]
        assert "No confident identification" in data["identification"]
        assert data["confidence"] <= 0.20
        assert data["is_confident"] is False
        assert data["fallback_warning"] is not None
