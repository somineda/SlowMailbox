import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from models import Letter
from scheduler import check_and_send_letters_async


@pytest.mark.asyncio
async def test_check_and_send_letters_first_send():
    """Test checking and sending first letters (7 days)"""
    # Create a letter that should be sent (past send_at time)
    now = datetime.now(timezone.utc)
    past_time = now - timedelta(minutes=5)

    letter = await Letter.create(
        recipient_email="test@example.com",
        content="Test letter",
        send_at=past_time,
        second_send_at=now + timedelta(days=23),
        sent=False
    )

    # Mock send_email to avoid actual email sending
    with patch('scheduler.send_email', return_value=True) as mock_send:
        await check_and_send_letters_async()

        # Check that send_email was called
        mock_send.assert_called_once()
        assert mock_send.call_args[0][0] == "test@example.com"
        assert mock_send.call_args[0][1] == "Test letter"
        assert mock_send.call_args[1]["is_second_send"] is False

    # Verify letter was marked as sent
    await letter.refresh_from_db()
    assert letter.sent is True
    assert letter.sent_at is not None


@pytest.mark.asyncio
async def test_check_and_send_letters_second_send():
    """Test checking and sending second letters (30 days)"""
    # Create a letter with first send done, second send due
    now = datetime.now(timezone.utc)
    past_time = now - timedelta(days=25)

    letter = await Letter.create(
        recipient_email="test@example.com",
        content="Test letter",
        send_at=past_time - timedelta(days=20),
        second_send_at=past_time,
        sent=True,
        sent_at=past_time - timedelta(days=20),
        second_sent=False
    )

    # Mock send_email
    with patch('scheduler.send_email', return_value=True) as mock_send:
        await check_and_send_letters_async()

        # Check that send_email was called with is_second_send=True
        assert mock_send.call_count >= 1
        # Find the call with is_second_send=True
        second_send_calls = [call for call in mock_send.call_args_list
                            if call[1].get("is_second_send") is True]
        assert len(second_send_calls) == 1

    # Verify letter was marked as second sent
    await letter.refresh_from_db()
    assert letter.second_sent is True
    assert letter.second_sent_at is not None


@pytest.mark.asyncio
async def test_check_and_send_letters_not_due():
    """Test that letters not yet due are not sent"""
    # Create a letter in the future
    now = datetime.now(timezone.utc)
    future_time = now + timedelta(days=5)

    letter = await Letter.create(
        recipient_email="test@example.com",
        content="Test letter",
        send_at=future_time,
        second_send_at=now + timedelta(days=28),
        sent=False
    )

    # Mock send_email
    with patch('scheduler.send_email', return_value=True) as mock_send:
        await check_and_send_letters_async()

        # send_email should not be called for this letter
        mock_send.assert_not_called()

    # Verify letter was not marked as sent
    await letter.refresh_from_db()
    assert letter.sent is False


@pytest.mark.asyncio
async def test_check_and_send_letters_already_sent():
    """Test that already sent letters are not sent again"""
    # Create a letter that was already sent
    now = datetime.now(timezone.utc)
    past_time = now - timedelta(days=10)

    letter = await Letter.create(
        recipient_email="test@example.com",
        content="Test letter",
        send_at=past_time,
        second_send_at=now + timedelta(days=20),
        sent=True,
        sent_at=past_time
    )

    # Mock send_email
    with patch('scheduler.send_email', return_value=True) as mock_send:
        await check_and_send_letters_async()

        # send_email should not be called for already sent letter
        mock_send.assert_not_called()


@pytest.mark.asyncio
async def test_check_and_send_letters_both_sends():
    """Test handling both first and second sends in one run"""
    now = datetime.now(timezone.utc)
    past_time = now - timedelta(minutes=5)

    # Create letter for first send
    letter1 = await Letter.create(
        recipient_email="first@example.com",
        content="First send letter",
        send_at=past_time,
        second_send_at=now + timedelta(days=23),
        sent=False
    )

    # Create letter for second send
    letter2 = await Letter.create(
        recipient_email="second@example.com",
        content="Second send letter",
        send_at=past_time - timedelta(days=23),
        second_send_at=past_time,
        sent=True,
        sent_at=past_time - timedelta(days=23),
        second_sent=False
    )

    # Mock send_email
    with patch('scheduler.send_email', return_value=True) as mock_send:
        await check_and_send_letters_async()

        # Should be called twice
        assert mock_send.call_count == 2


@pytest.mark.asyncio
async def test_check_and_send_letters_email_failure():
    """Test handling email sending failure"""
    now = datetime.now(timezone.utc)
    past_time = now - timedelta(minutes=5)

    letter = await Letter.create(
        recipient_email="test@example.com",
        content="Test letter",
        send_at=past_time,
        second_send_at=now + timedelta(days=23),
        sent=False
    )

    # Mock send_email to return False (failure)
    with patch('scheduler.send_email', return_value=False) as mock_send:
        await check_and_send_letters_async()

        mock_send.assert_called_once()

    # Letter should NOT be marked as sent on failure
    await letter.refresh_from_db()
    assert letter.sent is False
    assert letter.sent_at is None


@pytest.mark.asyncio
async def test_check_and_send_letters_exception_handling():
    """Test that exceptions don't crash the scheduler"""
    now = datetime.now(timezone.utc)
    past_time = now - timedelta(minutes=5)

    await Letter.create(
        recipient_email="test@example.com",
        content="Test letter",
        send_at=past_time,
        second_send_at=now + timedelta(days=23),
        sent=False
    )

    # Mock send_email to raise exception
    with patch('scheduler.send_email', side_effect=Exception("Test error")):
        # Should not raise exception
        try:
            await check_and_send_letters_async()
        except Exception:
            pytest.fail("check_and_send_letters_async raised an exception")
