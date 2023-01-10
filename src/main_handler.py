"""Main handler"""
import json
from .telegram import telegram_send_message


def handler(event, context):
    """Handler"""

    if event is None and context is None:
        return {"statusCode": 200, "body": "True"}

    if event.get("headers", {}).get("Content-Type") != "application/json":
        return {'statusCode': 200, 'body': 'True'}

    body = json.loads(event.get("body", "{}"))

    if not body:
        return {'statusCode': 200, 'body': 'True'}

    message = body["message"]
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]
    chat_type = message["chat"]["type"] # private, group, supergroup
    from_user_id = message["from"]["id"]
    from_user_first_name = message["from"]["first_name"]

    bot_command = None
    bot_command_args = []

    for entitie in message.get("entities", []):
        if entitie["type"] != "bot_command":
            continue
        bot_command = message["text"][entitie["offset" ] + 1 : entitie["length"]].lower()
        bot_command_args = message["text"][entitie["length"]:].split(' ')

    for entitie in message.get("caption_entities", []):
        if entitie["type"] != "bot_command":
            continue
        bot_command = message["caption"][entitie["offset" ] + 1 : entitie["length"]].lower()
        bot_command_args = message["caption"][entitie["length"]:].split(' ')

    if chat_type in ("group", "private"):
        if bot_command == "version":
            telegram_send_message(chat_id, "0.0.2", message_id)
            print(bot_command_args, from_user_id, from_user_first_name)
            return {"statusCode": 200, "body": "True"}

    return {"statusCode": 200, "body": "True"}
