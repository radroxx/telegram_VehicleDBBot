"""Test configs"""

import os
import base64
from .test_mock import create_facke_boto3_module
from .cache import cache_wipe_key
from .aws import aws_kms
from .config import (
    config_platerecognizer_api_key,
    config_telegram_url,
    config_telegram_file_url
)


create_facke_boto3_module()


def test_platerecognizer_api_key():
    """Test read platerecognizer api key"""
    test_data = base64.b64encode(b"Hello world 1").decode("UTF-8")
    os.environ["PLATERECOGNIZER_API"] = test_data

    assert config_platerecognizer_api_key() == "Hello world 1"


def test_telegram_url():
    """Test read telegram url"""
    test_data = base64.b64encode(b"hello_world_2").decode("UTF-8")
    os.environ["TELEGRAM_BOT_API"] = test_data

    assert config_telegram_url() == "https://api.telegram.org/bothello_world_2/"
    assert config_telegram_file_url() == "https://api.telegram.org/file/bothello_world_2/"


def test_platerecognizer_api_key_cache():
    """Test cache work in config"""

    test_data = base64.b64encode(b"Hello world 3").decode("UTF-8")
    os.environ["PLATERECOGNIZER_API"] = test_data
    cache_wipe_key("config_platerecognizer_api_key")

    client = aws_kms()
    decrypt_count = client.decrypt_count
    config_platerecognizer_api_key()
    config_platerecognizer_api_key()
    assert config_platerecognizer_api_key() == "Hello world 3"
    assert client.decrypt_count - decrypt_count == 1


def test_telegram_url_cache():
    """Test cache work in config"""

    test_data = base64.b64encode(b"hello_world_4").decode("UTF-8")
    os.environ["TELEGRAM_BOT_API"] = test_data
    cache_wipe_key("config_telegram_key")

    client = aws_kms()
    decrypt_count = client.decrypt_count
    config_telegram_url()
    config_telegram_url()
    assert config_telegram_url() == "https://api.telegram.org/bothello_world_4/"
    assert client.decrypt_count - decrypt_count == 1
