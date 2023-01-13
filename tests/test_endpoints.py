import os
import asyncio
import pytest

from mealieapi import Client

@pytest.fixture(scope="module")
def custom_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def client(custom_loop):
    async with Client(os.environ.get("HOMEASSISTANTAPI_URL", "http://localhost:9925")) as client:
        yield client


async def test_endpoint_api_about_info(client):
    """Test the app/about endpoint."""
    assert await client.about()

