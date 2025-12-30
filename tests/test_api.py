import pytest
from datetime import datetime, timezone, timedelta


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "느린 우체통" in data["message"]


@pytest.mark.asyncio
async def test_create_letter(client, sample_letter_data):
    """Test creating a new letter"""
    response = await client.post("/letters/", json=sample_letter_data)
    assert response.status_code == 200

    data = response.json()
    assert data["recipient_email"] == sample_letter_data["recipient_email"]
    assert data["content"] == sample_letter_data["content"]
    assert "id" in data
    assert "created_at" in data
    assert "send_at" in data
    assert "second_send_at" in data
    assert data["sent"] is False
    assert data["second_sent"] is False


@pytest.mark.asyncio
async def test_create_letter_with_invalid_email(client):
    """Test creating a letter with invalid email"""
    invalid_data = {
        "recipient_email": "invalid-email",
        "content": "Test content"
    }
    response = await client.post("/letters/", json=invalid_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_letters(client, create_sample_letter):
    """Test getting all letters"""
    response = await client.get("/letters/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_letter_by_id(client, create_sample_letter):
    """Test getting a specific letter by ID"""
    letter = await create_sample_letter
    response = await client.get(f"/letters/{letter.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == letter.id
    assert data["recipient_email"] == letter.recipient_email
    assert data["content"] == letter.content


@pytest.mark.asyncio
async def test_get_nonexistent_letter(client):
    """Test getting a letter that doesn't exist"""
    response = await client.get("/letters/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_letter_send_times(client, sample_letter_data):
    """Test that letter has correct send times (7 days and 30 days)"""
    response = await client.post("/letters/", json=sample_letter_data)
    assert response.status_code == 200

    data = response.json()
    send_at = datetime.fromisoformat(data["send_at"].replace("Z", "+00:00"))
    second_send_at = datetime.fromisoformat(data["second_send_at"].replace("Z", "+00:00"))

    # Check that send times are in the future
    now = datetime.now(timezone.utc)
    assert send_at > now
    assert second_send_at > now

    # Check that second send is after first send
    assert second_send_at > send_at


@pytest.mark.asyncio
async def test_get_letters_with_pagination(client):
    """Test getting letters with pagination"""
    # Create multiple letters
    from models import Letter
    now = datetime.now(timezone.utc)
    for i in range(5):
        await Letter.create(
            recipient_email=f"test{i}@example.com",
            content=f"Test content {i}",
            send_at=now + timedelta(days=7),
            second_send_at=now + timedelta(days=30)
        )

    # Test pagination
    response = await client.get("/letters/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2

    response = await client.get("/letters/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2
