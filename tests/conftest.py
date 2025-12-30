import pytest
import os
from tortoise import Tortoise
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta

# Set test environment
os.environ["DATABASE_URL"] = "sqlite://:memory:"

from main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def initialize_tests():
    """Initialize test database before each test"""
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["models"]}
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture
async def client():
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_letter_data():
    """Sample letter data for testing"""
    return {
        "recipient_email": "test@example.com",
        "content": "2025년 새해 다짐: 매일 운동하기!"
    }


@pytest.fixture
async def create_sample_letter():
    """Create a sample letter in database"""
    from models import Letter

    now = datetime.now(timezone.utc)
    letter = await Letter.create(
        recipient_email="test@example.com",
        content="테스트 편지 내용",
        send_at=now + timedelta(days=7),
        second_send_at=now + timedelta(days=30)
    )
    return letter
