import io
import pytest
from PIL import Image
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_identify_multipart_endpoint():
    # Generate in-memory PNG
    img = Image.new("RGB", (64, 64), color=(255, 215, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("flower.png", buf.getvalue(), "image/png")}
        data = {"user_hint": "Yellow wild flower"}
        response = await client.post("/api/identify", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert "identification" in result
        assert "outdoor_challenge" in result
        assert "screen_break_message" in result
        assert result["confidence"] > 0


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
