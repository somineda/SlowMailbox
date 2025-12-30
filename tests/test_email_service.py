import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
from email_service import get_random_png_image, send_email


def test_get_random_png_image_no_folder(tmp_path):
    """Test getting random PNG when folder doesn't exist"""
    # Test with non-existent folder
    with patch('email_service.os.path.dirname', return_value=str(tmp_path)):
        result = get_random_png_image()
        assert result is None


def test_get_random_png_image_empty_folder(tmp_path):
    """Test getting random PNG when folder is empty"""
    png_folder = tmp_path / "png"
    png_folder.mkdir()

    with patch('email_service.os.path.join', return_value=str(png_folder)):
        with patch('email_service.os.path.exists', return_value=True):
            with patch('email_service.os.listdir', return_value=[]):
                result = get_random_png_image()
                assert result is None


def test_get_random_png_image_success(tmp_path):
    """Test successfully getting a random PNG"""
    png_folder = tmp_path / "png"
    png_folder.mkdir()

    # Create test PNG files
    (png_folder / "test1.png").touch()
    (png_folder / "test2.png").touch()
    (png_folder / "test3.png").touch()

    with patch('email_service.os.path.dirname', return_value=str(tmp_path)):
        result = get_random_png_image()
        assert result is not None
        assert result.endswith('.png')


def test_get_random_png_image_filters_non_png(tmp_path):
    """Test that only PNG files are selected"""
    png_folder = tmp_path / "png"
    png_folder.mkdir()

    # Create various file types
    (png_folder / "image.png").touch()
    (png_folder / "image.jpg").touch()
    (png_folder / "document.txt").touch()

    with patch('email_service.os.path.dirname', return_value=str(tmp_path)):
        result = get_random_png_image()
        assert result is not None
        assert 'image.png' in result


@patch('email_service.smtplib.SMTP')
@patch('email_service.get_random_png_image')
def test_send_email_first_send(mock_get_image, mock_smtp):
    """Test sending first email (7 days)"""
    # Mock image
    mock_get_image.return_value = None

    # Mock SMTP
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    result = send_email("test@example.com", "Test content", is_second_send=False)

    assert result is True
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once()
    mock_server.send_message.assert_called_once()


@patch('email_service.smtplib.SMTP')
@patch('email_service.get_random_png_image')
def test_send_email_second_send(mock_get_image, mock_smtp):
    """Test sending second email (30 days)"""
    # Mock image
    mock_get_image.return_value = None

    # Mock SMTP
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    result = send_email("test@example.com", "Test content", is_second_send=True)

    assert result is True
    mock_server.send_message.assert_called_once()


@patch('email_service.smtplib.SMTP')
@patch('email_service.get_random_png_image')
@patch('builtins.open', new_callable=mock_open, read_data=b'fake image data')
def test_send_email_with_image(mock_file, mock_get_image, mock_smtp):
    """Test sending email with PNG attachment"""
    # Mock image path
    mock_get_image.return_value = "/fake/path/image.png"

    # Mock SMTP
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    result = send_email("test@example.com", "Test content")

    assert result is True
    mock_file.assert_called_once_with("/fake/path/image.png", 'rb')
    mock_server.send_message.assert_called_once()


@patch('email_service.smtplib.SMTP')
@patch('email_service.get_random_png_image')
def test_send_email_failure(mock_get_image, mock_smtp):
    """Test email sending failure"""
    # Mock image
    mock_get_image.return_value = None

    # Mock SMTP to raise exception
    mock_smtp.return_value.__enter__.side_effect = Exception("SMTP Error")

    result = send_email("test@example.com", "Test content")

    assert result is False


@patch('email_service.smtplib.SMTP')
@patch('email_service.get_random_png_image')
def test_send_email_content_difference(mock_get_image, mock_smtp):
    """Test that first and second emails have different content"""
    mock_get_image.return_value = None
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    # Send first email
    send_email("test@example.com", "Content", is_second_send=False)
    first_call = mock_server.send_message.call_args

    # Send second email
    mock_server.reset_mock()
    send_email("test@example.com", "Content", is_second_send=True)
    second_call = mock_server.send_message.call_args

    # The messages should be different
    assert first_call != second_call
