"""Main handler"""
import json
from .cache import cache_init
from .telegram import telegram_send_message
from .database import _db_create_tables


def handler(event, context):
    """Handler"""

    if event is None and context is None:
        return {"statusCode": 200, "body": "True"}

    if event.get("headers", {}).get("Content-Type") != "application/json":
        return {'statusCode': 200, 'body': 'True'}

    body = json.loads(event.get("body", "{}"))

    if not body:
        return {'statusCode': 200, 'body': 'True'}

    cache_init()
    _db_create_tables()

    message = body["message"]
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]
    chat_type = message["chat"]["type"] # private, group, supergroup
    from_user_id = message["from"]["id"]
    from_user_first_name = message["from"]["first_name"]

    # Bot command extract
    bot_command = None
    bot_command_args = []

    for entitie in message.get("entities", []):
        if entitie["type"] != "bot_command":
            continue
        bot_command = message["text"][entitie["offset" ] + 1 : entitie["length"]].lower()
        bot_command_args = message["text"][entitie["length"] + 1:].split(' ')

    for entitie in message.get("caption_entities", []):
        if entitie["type"] != "bot_command":
            continue
        bot_command = message["caption"][entitie["offset" ] + 1 : entitie["length"]].lower()
        bot_command_args = message["caption"][entitie["length"] + 1:].split(' ')
    # Bot Command extract

    if chat_type in ("group", "private"):
        # /version
        if bot_command == "version":
            telegram_send_message(chat_id, "0.0.2", message_id)
            print(bot_command_args, from_user_id, from_user_first_name)
            return {"statusCode": 200, "body": "True"}

    if "photo" in message:
        pass

    return {"statusCode": 200, "body": "True"}
