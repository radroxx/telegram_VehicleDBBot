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
                {"AttributeName": "message_id", "AttributeType": 'N'},
            ],
            KeySchema = [
                {"AttributeName": "chat_id", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            LocalSecondaryIndexes = [{
                "IndexName": "check_log_message_id",
                "KeySchema": [
                    {"AttributeName": "chat_id", "KeyType": "HASH"},
                    {"AttributeName": "message_id", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"}
            }],
            ProvisionedThroughput = {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        )

    cache_write("database_create_tables", True, 2628000) # 1 month


def number_to_string(aws_obj):
    """conver all number to string"""
    for key in list(aws_obj.keys()):
        if 'N' not in aws_obj[key]:
            continue
        aws_obj[key] = {'N': str(aws_obj[key]['N'])}
    return aws_obj


def string_to_number(aws_obj, float_keys = None):
    """conver all number to number"""
    if float_keys is None:
        float_keys = []
    for item in aws_obj.items():
        if 'N' not in item[1]:
            continue
        if item[0] in float_keys:
            item[1]['N'] = float(item[1]['N'])
        else:
            item[1]['N'] = int(item[1]['N'])
    return aws_obj


def db_get_user(chat_id, user_id):
    """Get user from db"""

    db_response = aws_dynamodb().get_item(
        TableName = __USERS_TABLE_NAME,
        Key = {"chat_id": {'N': str(chat_id)}, "user_id": {'N': str(user_id)}}
    )
    item = {
        "chat_id": {'N': chat_id},
        "user_id": {'N': user_id},
        "raiting": {'N': 0}
    }
    if "Item" in db_response:
        item = db_response["Item"]

    return string_to_number(item)


def db_put_user(item):
    """Put user item to db"""

    aws_dynamodb().put_item(
        TableName = __USERS_TABLE_NAME,
        Item = number_to_string(item.copy())
    )

    return string_to_number(item)


def db_top_users(chat_id, top = 10):
    """Search top users"""

    data = aws_dynamodb().query(
        TableName = __USERS_TABLE_NAME,
        IndexName = "user_raiting",
        KeyConditionExpression = "#chat_id = :chat_id",
        ExpressionAttributeNames = {"#chat_id": "chat_id"},
        ExpressionAttributeValues = {":chat_id": {'N': str(chat_id)}},
        ScanIndexForward = False,
        Limit = top,
    )
    for item in data["Items"]:
        string_to_number(item)
    return data["Items"]


def db_get_vehicle_raiting(chat_id, plate):
    """Get vehicle raiting"""

    items = aws_dynamodb().get_item(
        TableName = __VEHICLE_RATING_TABLE_NAME,
        Key = {"chat_id": {'N': str(chat_id)}, "plate": {'S': str(plate)}}
    )
    item = {
        "chat_id": {'N': chat_id},
        "plate": {'S': plate},
        "raiting": {'N': 0},
        "first_check": {'N': 0},
        "last_check": {'N': 0}
    }
    if "Item" in items:
        item = items["Item"]

    return string_to_number(item, ["first_check", "last_check"])


def db_put_vehicle_raiting(item):
    """Put user item to db"""

    aws_dynamodb().put_item(
        TableName = __VEHICLE_RATING_TABLE_NAME,
        Item = number_to_string(item.copy())
    )
    return item


def db_top_vehicles(chat_id, top = 10):
    """Search top vehicles"""

    data = aws_dynamodb().query(
        TableName = __VEHICLE_RATING_TABLE_NAME,
        IndexName = "vehicle_raiting",
        KeyConditionExpression = "#chat_id = :chat_id",
        ExpressionAttributeNames = {"#chat_id": "chat_id"},
        ExpressionAttributeValues = {":chat_id": {'N': str(chat_id)}},
        ScanIndexForward = False,
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
        "images_file_uid": {'L': []},
        "show_images": {'L': []},
        "is_hiden": {"BOOL": False}
    }
    if "Item" in items:
        item = items["Item"]
    return item


def db_put_vehicle(item):
    """Put vehicle item to db"""

    aws_dynamodb().put_item(TableName = __VEHICLE_TABLE_NAME, Item = item)
    return item


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
    return item


def db_get_checks_log(chat_id, timestamp):
    """Scan table and return ordering check logs"""

    items = aws_dynamodb().get_item(
        TableName = __CHECK_LOGS_TABLE_NAME,
        Key = {"chat_id": {'N': str(chat_id)}, "timestamp": {'N': str(timestamp)}},
    )

    item = {
        "chat_id": {'N': str(chat_id)},
        "timestamp": {'N': 0},
        "prev_timestamp": {'N': 0},
        "message_id": {'N': 0},
        "plate": {'S': None},
        "dscore": {'N': 0},
        "user_id": {'N': 0},
        "user_raiting_diff": {'N': 0},
        "user_raiting_current": {'N': 0},
        "is_show_reply": {"BOOL": False},
    }

    if "Item" in items:
        item = items["Item"]

    return string_to_number(item, ["timestamp", "prev_timestamp", "dscore"])


def db_put_checks_log(item):
    """Put check log"""

    aws_dynamodb().put_item(
        TableName = __CHECK_LOGS_TABLE_NAME,
        Item = number_to_string(item.copy())
    )

    return item


def db_get_checks_log_by_messae_id(chat_id, message_id):
    """Find check logs by message_id"""
    data = aws_dynamodb().query(
        TableName = __CHECK_LOGS_TABLE_NAME,
        IndexName = "check_log_message_id",
        KeyConditionExpression = "#chat_id = :chat_id and #message_id = :message_id",
        ExpressionAttributeNames = {"#chat_id": "chat_id", "#message_id": "message_id"},
        ExpressionAttributeValues = {
            ":chat_id": {'N': str(chat_id)},
            ":message_id": {'N': str(message_id)}
        },
        ScanIndexForward = False,
        Limit = 1000,
    )
    for item in data["Items"]:
        string_to_number(item, ["timestamp", "prev_timestamp", "dscore"])
    return data["Items"]


def db_create_checks_log( # pylint: disable=R0913
    chat_id, timestamp, prev_timestamp, message_id, plate, dscore,
    user_id, raiting_diff, raiting_current, is_show_reply):
    """Put check log, timestamp with ns becose chat_id + timestamp is FK"""

    item = {
        "chat_id": {'N': str(chat_id)},
        "timestamp": {'N': str(timestamp)},
        "prev_timestamp": {'N': str(prev_timestamp)},
        "message_id": {'N': str(message_id)},
        "plate": {'S': plate},
        "dscore": {'N': str(dscore)},
        "user_id": {'N': user_id},
        "user_raiting_diff": {'N': raiting_diff},
        "user_raiting_current": {'N': raiting_current},
        "is_show_reply": {"BOOL": is_show_reply},
    }

    return db_put_checks_log(item)


def db_seach_plate(plate_contains, chat_id = None, limit = 10):
    """Search vehicle by plate"""
    if len(plate_contains) == 0:
        return []

    expression = ""
    name_attr = {"#plate": "plate"}
    value_attr = {}

    if chat_id:
        name_attr["#chat_id"] = "chat_id"
        value_attr[":chat_id"] = {'N': str(chat_id)}
        expression = "#chat_id = :chat_id"

    index = 0
    for plate in plate_contains:
        value_attr[":v" + str(index)] = {'S': plate}
        if len(expression) > 0:
            expression += " AND "
        expression += "contains(#plate, :v" + str(index) + ")"

    data = aws_dynamodb().scan(
        TableName = __VEHICLE_RATING_TABLE_NAME,
        FilterExpression = expression,
        ExpressionAttributeNames = name_attr,
        ExpressionAttributeValues = value_attr,
        Limit = limit
    )

    return data.get("Items", [])
