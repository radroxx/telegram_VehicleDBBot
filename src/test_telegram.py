"""Test telegram module"""

import os
import base64
import urllib3
from .cache import cache_wipe_key
from .test_mock import mock_request
from .telegram import (
    telegram_send_message,
    telegram_send_photo,
    telegram_get_file_url,
    telegram_get_chat_member_first_name,
)


TELEGRAM_BOT_API = base64.b64encode(b"api").decode("UTF-8")

urllib3_poolmanager_request = urllib3.PoolManager.request

def setup_module(module): # pylint: disable=W0613
    """Init"""
    os.environ["TELEGRAM_BOT_API"] = TELEGRAM_BOT_API
    cache_wipe_key("config_telegram_key")


def teardown_module(module): # pylint: disable=W0613
    """Return original requests method"""
    urllib3.PoolManager.request = urllib3_poolmanager_request


def test_telegram_send_message():
    """Test send message"""
    def test_request(method, url, fields, headers, **urlopen_kw): # pylint: disable=W0613
        assert "chat_id" in fields
        assert "text" in fields
        assert "parse_mode" in fields
        assert fields["chat_id"] == -1
        assert fields["parse_mode"] == "html"
        assert url == "https://api.telegram.org/botapi/sendMessage"

    urllib3.PoolManager.request = mock_request(201, '{"ok":true}', test_request)

    data = telegram_send_message(-1, "Hello world 1")

    assert "ok" in data
    assert data["ok"] is True


def test_telegram_send_message_reply_to_message_id():
    """Test send message reply to"""
    def test_request(method, url, fields, headers, **urlopen_kw): # pylint: disable=W0613
        assert "reply_to_message_id" in fields
        assert fields["reply_to_message_id"] == 10

    urllib3.PoolManager.request = mock_request(200, '{"ok":true}', test_request)

    data = telegram_send_message(-1, "Hello world 1", 10)

    assert "ok" in data
    assert data["ok"] is True


def test_telegram_send_photo():
    """Test send photo"""
    def test_request(method, url, fields, headers, **urlopen_kw): # pylint: disable=W0613
        assert "chat_id" in fields
        assert "photo" in fields
        assert fields["photo"] == \
            "AgACAgIAAxkBAAIDg2O8lSrfe6ZdstytH9IKfiOpzvOJAAK2wjEbKGbpSdINZ0VFGROrAQADAgADeQADLQQ"
        assert url == "https://api.telegram.org/botapi/sendPhoto"

    urllib3.PoolManager.request = mock_request(200, '{"ok":true}', test_request)

    data = telegram_send_photo(
        -1,
        "AgACAgIAAxkBAAIDg2O8lSrfe6ZdstytH9IKfiOpzvOJAAK2wjEbKGbpSdINZ0VFGROrAQADAgADeQADLQQ"
    )

    assert "ok" in data
    assert data["ok"] is True


def test_telegram_send_photos():
    """Test send multi photo"""
    def test_request(method, url, fields, headers, **urlopen_kw): # pylint: disable=W0613
        assert "chat_id" in fields
        assert "media" in fields
        assert url == "https://api.telegram.org/botapi/sendMediaGroup"

    urllib3.PoolManager.request = mock_request(200, '{"ok":true}', test_request)

    data = telegram_send_photo(
        -1,
        [
            "AgACAgIAAxkBAAIDg2O8lSrfe6ZdstytH9IKfiOpzvOJAAK2wjEbKGbpSdINZ0VFGROrAQADAgADeQADLQQ",
            "AgACAgIAAxkBAAIDfWO8ohWHTqdK8GRNjh7DzIIO8u1VAAK1wjEbKGbpSWJmkiwhmNPIAQADAgADeQADLQQ"
        ]
    )

    assert "ok" in data
    assert data["ok"] is True


def test_telegram_send_photo_reply():
    """Test send photo reply"""
    def test_request(method, url, fields, headers, **urlopen_kw): # pylint: disable=W0613
        assert "chat_id" in fields
        assert "photo" in fields
        assert "reply_to_message_id" in fields
        assert fields["photo"] == \
            "AgACAgIAAxkBAAIDg2O8lSrfe6ZdstytH9IKfiOpzvOJAAK2wjEbKGbpSdINZ0VFGROrAQADAgADeQADLQQ"
        assert fields["reply_to_message_id"] == 10
        assert url == "https://api.telegram.org/botapi/sendPhoto"

    urllib3.PoolManager.request = mock_request(200, '{"ok":true}', test_request)

    data = telegram_send_photo(
        -1,
        "AgACAgIAAxkBAAIDg2O8lSrfe6ZdstytH9IKfiOpzvOJAAK2wjEbKGbpSdINZ0VFGROrAQADAgADeQADLQQ",
        reply_to_message_id=10
    )

    assert "ok" in data
    assert data["ok"] is True


def test_telegram_send_photo_text():
    """Test description photo"""
    def test_request(method, url, fields, headers, **urlopen_kw): # pylint: disable=W0613
        assert "chat_id" in fields
        assert "photo" in fields
        assert "caption" in fields
        assert fields["photo"] == \
            "AgACAgIAAxkBAAIDg2O8lSrfe6ZdstytH9IKfiOpzvOJAAK2wjEbKGbpSdINZ0VFGROrAQADAgADeQADLQQ"
        assert fields["caption"] == "Hello"
        assert url == "https://api.telegram.org/botapi/sendPhoto"

    urllib3.PoolManager.request = mock_request(200, '{"ok":true}', test_request)

    data = telegram_send_photo(
        -1,
        "AgACAgIAAxkBAAIDg2O8lSrfe6ZdstytH9IKfiOpzvOJAAK2wjEbKGbpSdINZ0VFGROrAQADAgADeQADLQQ",
        caption="Hello"
    )

    assert "ok" in data
    assert data["ok"] is True


def test_telegram_get_file_url():
    """Test get file url"""

    def test_request(method, url, fields, headers, **urlopen_kw): # pylint: disable=W0613
        assert "file_id" in fields
        assert fields["file_id"] == \
            "AgACAgIAAxkBAAIDg2O8lSrfe6ZdstytH9IKfiOpzvOJAAK2wjEbKGbpSdINZ0VFGROrAQADAgADeQADLQQ"
        assert url == "https://api.telegram.org/botapi/getFile"

    urllib3.PoolManager.request = mock_request(
        200,
        '{"result":{"file_path": "photos/file_651.jpg"}}',
        test_request
    )

    file = telegram_get_file_url(
        "AgACAgIAAxkBAAIDg2O8lSrfe6ZdstytH9IKfiOpzvOJAAK2wjEbKGbpSdINZ0VFGROrAQADAgADeQADLQQ"
    )

    assert file == "https://api.telegram.org/file/botapi/photos/file_651.jpg"


def test_telegram_get_chat_member_first_name():
    """Test get user name"""

    def test_request(method, url, fields, headers, **urlopen_kw): # pylint: disable=W0613
        assert "chat_id" in fields
        assert "user_id" in fields
        assert fields["chat_id"] == -1
        assert fields["user_id"] == 2
        assert url == "https://api.telegram.org/botapi/getChatMember"

    urllib3.PoolManager.request = mock_request(
        200,
        '{"result":{"user":{"first_name": "test"}}}',
        test_request
    )

    data = telegram_get_chat_member_first_name(-1, 2)

    assert data == "test"
