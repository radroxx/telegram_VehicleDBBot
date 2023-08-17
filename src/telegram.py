"""Telegram modules"""
import json
import hashlib
import urllib3
from .config import config_telegram_url, config_telegram_file_url


def _telegram_api(method, chat_id, fields, reply_to_message_id = None):
    """Send request to telegram"""

    if chat_id:
        fields["chat_id"] = chat_id

    if "text" in fields:
        fields["parse_mode"] = "html"

    if reply_to_message_id:
        fields["reply_to_message_id"] = reply_to_message_id

    with urllib3.PoolManager() as pool:
        response = pool.request(
            "POST", config_telegram_url() + method,
            fields=fields
        )
        return json.loads(response.data) # pylint: disable=E1101


def telegram_send_message(chat_id, text, reply_to_message_id = None):
    """Send message to telegram"""

    return _telegram_api("sendMessage", chat_id, {"text": text}, reply_to_message_id)


def telegram_send_photo(chat_id, photos, reply_to_message_id = None):
    """Send one photo or media group"""

    fields = {}

    if isinstance(photos, list):
        media = []
        for photo in photos:
            media.append({"type": "photo", "media": photo})
            if len(media) > 9:
                fields["media"] = json.dumps(media)
                _telegram_api("sendMediaGroup", chat_id, fields, reply_to_message_id)
                media = []

        fields["media"] = json.dumps(media)
        return _telegram_api("sendMediaGroup", chat_id, fields, reply_to_message_id)

    fields["photo"] = photos
    return _telegram_api("sendPhoto", chat_id, fields, reply_to_message_id)


def telegram_get_chat_member_first_name(chat_id, user_id):
    """Get user description"""

    data = _telegram_api("getChatMember", chat_id, {"user_id": user_id})
    return data.get("result", {}).get("user", {}).get("first_name", user_id)


def telegram_get_file_url(file_id):
    """Get file full path"""

    data = _telegram_api("getFile", chat_id = None, fields={"file_id": file_id})
    return config_telegram_file_url() + data["result"]["file_path"]


def telegram_get_file_sha1(file_url):
    """Return sha1 from file url"""

    sha1 = hashlib.sha1()

    with urllib3.PoolManager() as pool:
        response = pool.request("GET", file_url, preload_content=False)

        for chunc in response.stream(65535):
            sha1.update(chunc)

        return sha1.hexdigest()


def telegram_delete_message(chat_id, message_id):
    return _telegram_api("deleteMessage", chat_id, {"message_id": message_id})
