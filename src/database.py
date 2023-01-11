"""Database methods"""

from .cache import cache_write, cache_exists
from .aws import aws_dynamodb


__USERS_TABLE_NAME = "vehicledbbot_users"
__VEHICLE_TABLE_NAME = "vehicledbbot_vehicles"
__VEHICLE_IMAGES_TABLE_NAME = "vehicledbbot_vehicles_images"
__VEHICLE_RATING_TABLE_NAME = "vehicledbbot_vehicles_rating"
__CHECK_LOGS_TABLE_NAME = "vehicledbbot_check_logs"


def _db_create_tables():
    """Create tables"""

    if cache_exists("database_create_tables"):
        return

    dynamo_db = aws_dynamodb()
    tables = dynamo_db.list_tables()["TableNames"]
    if __USERS_TABLE_NAME not in tables:
        dynamo_db.create_table(
            TableName = __USERS_TABLE_NAME,
            AttributeDefinitions = [
                {"AttributeName": "chat_id", "AttributeType": 'N'},
                {"AttributeName": "user_id", "AttributeType": 'N'},
                {"AttributeName": "raiting", "AttributeType": 'N'},
            ],
            KeySchema = [
                {"AttributeName": "chat_id", "KeyType": "HASH"},
                {"AttributeName": "user_id", "KeyType": "RANGE"},
            ],
            LocalSecondaryIndexes = [{
                "IndexName": "user_raiting",
                "KeySchema": [
                    {"AttributeName": "chat_id", "KeyType": "HASH"},
                    {"AttributeName": "raiting", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"}
            }],
            ProvisionedThroughput = {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        )

    if __VEHICLE_RATING_TABLE_NAME not in tables:
        dynamo_db.create_table(
            TableName = __VEHICLE_RATING_TABLE_NAME,
            AttributeDefinitions = [
                {"AttributeName": "chat_id", "AttributeType": 'N'},
                {"AttributeName": "plate", "AttributeType": 'S'},
                {"AttributeName": "raiting", "AttributeType": 'N'},
            ],
            KeySchema = [
                {"AttributeName": "chat_id", "KeyType": "HASH"},
                {"AttributeName": "plate", "KeyType": "RANGE"},
            ],
            LocalSecondaryIndexes = [{
                "IndexName": "vehicle_raiting",
                "KeySchema": [
                    {"AttributeName": "chat_id", "KeyType": "HASH"},
                    {"AttributeName": "raiting", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"}
            }],
            ProvisionedThroughput = {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        )

    if __VEHICLE_TABLE_NAME not in tables:
        dynamo_db.create_table(
            TableName = __VEHICLE_TABLE_NAME,
            AttributeDefinitions = [{"AttributeName": "plate", "AttributeType": 'S'}],
            KeySchema = [{"AttributeName": "plate", "KeyType": "HASH"}],
            ProvisionedThroughput = {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        )

    if __VEHICLE_IMAGES_TABLE_NAME not in tables:
        dynamo_db.create_table(
            TableName = __VEHICLE_IMAGES_TABLE_NAME,
            AttributeDefinitions = [
                {"AttributeName": "image", "AttributeType": 'S'}
            ],
            KeySchema = [
                {"AttributeName": "image", "KeyType": "HASH"}
            ],
            ProvisionedThroughput = {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        )

    if __CHECK_LOGS_TABLE_NAME not in tables:
        dynamo_db.create_table(
            TableName = __CHECK_LOGS_TABLE_NAME,
            AttributeDefinitions = [
                {"AttributeName": "chat_id", "AttributeType": 'N'},
                {"AttributeName": "timestamp", "AttributeType": 'N'},
            ],
            KeySchema = [
                {"AttributeName": "chat_id", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            ProvisionedThroughput = {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        )

    cache_write("database_create_tables", True, 2628000) # 1 month


def db_get_user(chat_id, user_id):
    """Get user from db"""

    items = aws_dynamodb().get_item(
        TableName = __USERS_TABLE_NAME,
        Key = {"chat_id": {'N': str(chat_id)}, "user_id": {'N': str(user_id)}}
    )
    item = {
        "chat_id": {'N': chat_id},
        "user_id": {'N': user_id},
        "raiting": {'N': 0}
    }
    if "Item" in items:
        item = items["Item"]
    item["chat_id"]['N'] = int(item["chat_id"]['N'])
    item["user_id"]['N'] = int(item["user_id"]['N'])
    item["raiting"]['N'] = int(item["raiting"]['N'])
    return item


def db_put_user(item):
    """Put user item to db"""
    item["chat_id"]['N'] = str(item["chat_id"]['N'])
    item["user_id"]['N'] = str(item["user_id"]['N'])
    item["raiting"]['N'] = str(item["raiting"]['N'])

    aws_dynamodb().put_item(TableName = __USERS_TABLE_NAME, Item = item)


def db_top_users(chat_id, top = 10):
    """Search top users"""

    data = aws_dynamodb().query(
        TableName = __USERS_TABLE_NAME,
        IndexName = "user_raiting",
        KeyConditionExpression = "#chat_id = :chat_id",
        ExpressionAttributeNames = {"#chat_id": "chat_id"},
        ExpressionAttributeValues = {":chat_id": {'N': str(chat_id)}},
        ScanIndexForward = True,
        Limit = top,
    )
    for item in data["Items"]:
        item["chat_id"]['N'] = int(item["chat_id"]['N'])
        item["user_id"]['N'] = int(item["user_id"]['N'])
        item["raiting"]['N'] = int(item["raiting"]['N'])
    return data["Items"]


def db_get_vehicle_raiting(chat_id, plate):
    """Get vehicle raiting"""

    items = aws_dynamodb().get_item(
        TableName = __USERS_TABLE_NAME,
        Key = {"chat_id": {'N': str(chat_id)}, "plate": {'S': str(plate)}}
    )
    item = {
        "chat_id": {'N': chat_id},
        "plate": {'S': plate},
        "raiting": {'N': 0}
    }
    if "Item" in items:
        item = items["Item"]
    item["chat_id"]['N'] = int(item["chat_id"]['N'])
    item["raiting"]['N'] = int(item["raiting"]['N'])
    return item


def db_put_vehicle_raiting(item):
    """Put user item to db"""
    item["chat_id"]['N'] = str(item["chat_id"]['N'])
    item["raiting"]['N'] = str(item["raiting"]['N'])

    aws_dynamodb().put_item(TableName = __VEHICLE_RATING_TABLE_NAME, Item = item)


def db_top_vehicles(chat_id, top = 10):
    """Search top vehicles"""

    data = aws_dynamodb().query(
        TableName = __VEHICLE_RATING_TABLE_NAME,
        IndexName = "vehicle_raiting",
        KeyConditionExpression = "#chat_id = :chat_id",
        ExpressionAttributeNames = {"#chat_id": "chat_id"},
        ExpressionAttributeValues = {":chat_id": {'N': str(chat_id)}},
        ScanIndexForward = True,
        Limit = top,
    )
    for item in data["Items"]:
        item["chat_id"]['N'] = int(item["chat_id"]['N'])
        item["raiting"]['N'] = int(item["raiting"]['N'])
    return data["Items"]


def db_get_vehicle(plate):
    """Get vehicle by plate"""

    items = aws_dynamodb().get_item(
        TableName = __VEHICLE_TABLE_NAME,
        Key = {"plate": {'S': plate}}
    )
    item = {
        "plate": {'S': plate},
        "show_images": {'L': []},
    }
    if "Item" in items:
        item = items["Item"]
    return item


def db_put_vehicle(item):
    """Put vehicle item to db"""

    aws_dynamodb().put_item(TableName = __VEHICLE_TABLE_NAME, Item = item)


def db_get_vehicle_image(image_id):
    """Get vehicle image"""

    items = aws_dynamodb().get_item(
        TableName = __VEHICLE_IMAGES_TABLE_NAME,
        Key = {"image": {'S': image_id}}
    )
    item = {
        "image": {'S': image_id},
        "plates": {'L': []},
    }
    if "Item" in items:
        item = items["Item"]
    return item


def db_put_vehicle_image(item):
    """Put vehicle item"""

    aws_dynamodb().put_item(TableName = __VEHICLE_IMAGES_TABLE_NAME, Item = item)


def db_query_checks_log(chat_id, plate, order = "asc", limit = 1):
    """Scan table and return ordering check logs"""

    scan_index_forward = False
    if order == "desc":
        scan_index_forward = True

    data = aws_dynamodb().query(
        TableName = __CHECK_LOGS_TABLE_NAME,
        KeyConditionExpression = "#chat_id = :chat_id and #plate = :plate",
        ExpressionAttributeNames = {"#chat_id": "chat_id", "#plate": "plate"},
        ExpressionAttributeValues = {
            ":chat_id": {'N': str(chat_id)},
            ":plate": {'S': plate}
        },
        ScanIndexForward = scan_index_forward,
        Limit = limit,
    )
    for item in data["Items"]:
        item["chat_id"]['N'] = int(item["chat_id"]['N'])
        item["user_id"]['N'] = int(item["user_id"]['N'])
        item["timestamp"]['N'] = int(item["timestamp"]['N'])
        item["message_id"]['N'] = int(item["message_id"]['N'])
    return data["Items"]


def db_get_checks_log_first(chat_id, plate):
    """Get first check log by plate"""
    return db_query_checks_log(chat_id, plate, "asc", 1)


def db_get_checks_log_last(chat_id, plate):
    """Get last check log by plate"""
    return db_query_checks_log(chat_id, plate, "desc", 1)


def db_put_checks_log( # pylint: disable=R0913
    chat_id, timestamp, plate,
    user_id, message_id, is_show_reply = True):
    """Put check log, timestamp with ns becose chat_id + timestamp is FK"""
    item = {
        "chat_id": {'N': str(chat_id)},
        "timestamp": {'N': str(timestamp)},
        "plate": {'S': plate},
        "user_id": {'N': str(user_id)},
        "message_id": {'N': str(message_id)},
        "is_show_reply": {"BOOL": is_show_reply}
    }

    aws_dynamodb().put_item(TableName = __CHECK_LOGS_TABLE_NAME, Item = item)
