import pytest
from httpx import AsyncClient, ASGITransport
from ccam_backend.main import app
from ccam_backend.config import settings


@pytest.fixture
def test_settings():
    return settings


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
