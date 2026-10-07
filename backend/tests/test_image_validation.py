import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_invalid_image_type():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("malicious.exe", b"NOT_AN_IMAGE", "application/octet-stream")}
        res = await client.post("/api/identify", files=files)
        assert res.status_code == 415


@pytest.mark.asyncio
async def test_corrupt_image_bytes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("corrupt.png", b"CORRUPTED_BYTES_HERE", "image/png")}
        res = await client.post("/api/identify", files=files)
        assert res.status_code == 400
        assert "Invalid image" in res.json()["detail"]
