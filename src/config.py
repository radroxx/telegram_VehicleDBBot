"""Configs module"""

import os
from .cache import cache_read, cache_exists, cache_write
from .aws import aws_kms_decrypt


def _config_telegram_bot_key():
    """Return telegram bot api key"""
    if cache_exists("config_telegram_key"):
        return cache_read("config_telegram_key")

    telegram_key = aws_kms_decrypt(os.getenv("TELEGRAM_BOT_API"))
    cache_write("config_telegram_key", telegram_key)
    return telegram_key


def config_telegram_url():
    """Retrun full telegram url"""

    return "".join([
        "https://api.telegram.org/bot",
        _config_telegram_bot_key(),
        "/"
    ])


def config_telegram_file_url():
    """Retrun full telegram url"""

    return "".join([
        "https://api.telegram.org/file/bot",
        _config_telegram_bot_key(),
        "/"
    ])


def config_platerecognizer_api_key():
    """Retrun platerecognizer api key"""

    if cache_exists("config_platerecognizer_api_key"):
        return cache_read("config_platerecognizer_api_key")

    platerecognizer_api_key = aws_kms_decrypt(os.getenv("PLATERECOGNIZER_API"))

    cache_write("config_platerecognizer_api_key", platerecognizer_api_key)
    return platerecognizer_api_key
