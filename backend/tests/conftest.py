import pytest
from httpx import AsyncClient, ASGITransport
from ccam_backend.main import app, lifespan
from ccam_backend.config import settings


@pytest.fixture
def test_settings():
    return settings


@pytest.fixture(scope="module")
def lifespan_context():
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ctx = lifespan(app)
    try:
        loop.run_until_complete(ctx.__aenter__())
        yield
        try:
            loop.run_until_complete(ctx.__aexit__(None, None, None))
        except RuntimeError:
            pass
    finally:
        loop.close()


@pytest.fixture
async def client(lifespan_context):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
