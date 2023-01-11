"""Test database methods"""

from boto3 import DynamoDB
from .database import (
    _db_create_tables,
    db_get_user,
    db_put_user,
    db_get_vehicle_raiting,
    db_put_vehicle_raiting,
    db_get_vehicle,
    db_put_vehicle,
    db_get_vehicle_image,
    db_put_vehicle_image,
    db_top_users,
    db_top_vehicles,
    db_put_checks_log,
    db_get_checks_log_first,
    db_get_checks_log_last
)


def test_db_create():
    """Test read vehicle by plate"""

    def create_table(self, *args, **kwargs): # pylint: disable=W0613
        assert kwargs["TableName"] in (
            "vehicledbbot_users",
            "vehicledbbot_vehicles",
            "vehicledbbot_vehicles_images",
            "vehicledbbot_vehicles_rating",
            "vehicledbbot_check_logs"
        )
        assert "AttributeDefinitions" in kwargs
        assert "KeySchema" in kwargs
        assert "ProvisionedThroughput" in kwargs

    DynamoDB.create_table = create_table

    _db_create_tables()


def test_db_get_user():
    """Test get user"""

    user = db_get_user(0, 1)

    assert user["chat_id"]["N"] == 0
    assert user["user_id"]["N"] == 1
    assert user["raiting"]["N"] == 0


def test_db_put_user():
    """Test get user"""

    user = db_get_user(0, 1)

    user["raiting"]["N"] += 1

    db_put_user(user)

    user = db_get_user(0, 1)

    assert user["chat_id"]["N"] == 0
    assert user["user_id"]["N"] == 1
    assert user["raiting"]["N"] == 1


def test_db_get_vehicle_raiting():
    """Test get vr"""

    vehicle_raiting = db_get_vehicle_raiting(0, "[GB] 5H43H")

    assert vehicle_raiting["chat_id"]["N"] == 0
    assert vehicle_raiting["plate"]["S"] == "[GB] 5H43H"
    assert vehicle_raiting["raiting"]["N"] == 0


def test_db_put_vehicle_raiting():
    """Test put vr"""

    vehicle_raiting = db_get_vehicle_raiting(0, "[GB] 5H43H")

    vehicle_raiting["raiting"]["N"] += 2

    db_put_vehicle_raiting(vehicle_raiting)

    vehicle_raiting = db_get_vehicle_raiting(0, "[GB] 5H43H")

    assert vehicle_raiting["chat_id"]["N"] == 0
    assert vehicle_raiting["plate"]["S"] == "[GB] 5H43H"
    assert vehicle_raiting["raiting"]["N"] == 2


def test_db_get_vehicle():
    """Test get vehicle"""

    vehicle = db_get_vehicle("[GB] 5H43H")

    assert vehicle["plate"]["S"] == "[GB] 5H43H"
    assert vehicle["show_images"]["L"] == []
    assert vehicle["is_hiden"]["BOOL"] is False


def test_db_put_vehicle():
    """Test put vr"""

    vehicle = db_get_vehicle("[GB] 5H43H")
    vehicle["is_hiden"]["BOOL"] = True
    vehicle["show_images"]["L"].append({"S": "test"})

    db_put_vehicle(vehicle)

    vehicle = db_get_vehicle("[GB] 5H43H")

    assert vehicle["plate"]["S"] == "[GB] 5H43H"
    assert vehicle["is_hiden"]["BOOL"] is True
    assert len(vehicle["show_images"]["L"]) > 0


def test_db_get_vehicle_image():
    """Test get vehicle image"""

    vehicle_image = db_get_vehicle_image("my_image_id")

    assert vehicle_image["image"]["S"] == "my_image_id"
    assert vehicle_image["plates"]["L"] == []


def test_db_put_vehicle_image():
    """Test put vehicle image"""

    vehicle_image = db_get_vehicle_image("my_image_id")
    vehicle_image["plates"]["L"].append({'S': "test_plate"})

    db_put_vehicle_image(vehicle_image)

    vehicle_image = db_get_vehicle_image("my_image_id")

    assert vehicle_image["image"]["S"] == "my_image_id"
    assert vehicle_image["plates"]['L'][0]['S'] == "test_plate"


def test_db_top_users():
    """Test get top users"""
    for user_id in [400, 110, 503, 804, 105]:
        user = db_get_user(-1, user_id)
        user["raiting"]['N'] = int(user_id/100)
        db_put_user(user)

    top_list = db_top_users(-1, 3)
    assert len(top_list) == 3
    assert top_list[0]["user_id"]['N'] == 804
    assert top_list[1]["user_id"]['N'] == 503
    assert top_list[2]["user_id"]['N'] == 400


def test_db_top_vehicles():
    """Test get top vehicles"""
    for vehicle_raiting in [("0001", 1), ("0002", 1), ("1003", 10), ("2002", 8), ("43123", 5)]:
        vehicle_raiting_from_db = db_get_vehicle_raiting(-1, vehicle_raiting[0])
        vehicle_raiting_from_db["raiting"]['N'] = vehicle_raiting[1]
        db_put_vehicle_raiting(vehicle_raiting_from_db)

    top_list = db_top_vehicles(-1, 3)
    assert len(top_list) == 3
    assert top_list[0]["plate"]['S'] == "1003"
    assert top_list[1]["plate"]['S'] == "2002"
    assert top_list[2]["plate"]['S'] == "43123"


def test_db_put_checks_log():
    """Test check logs table"""
    db_put_checks_log(-10, 11, "0001", 30, 428364, True)
    db_put_checks_log(-10, 10, "0001", 20, 231432, True)
    db_put_checks_log(-10, 14, "0001", 40, 457594, True)
    db_put_checks_log(-10, 12, "0001", 30, 428364, True)
    db_put_checks_log(-11, 11, "0001", 50, 312556, True)
    db_put_checks_log(-11, 12, "0001", 60, 876657, True)
    db_put_checks_log(-11, 13, "0002", 50, 656345, True)
    db_put_checks_log(-11, 14, "0002", 60, 743523, True)

    first = db_get_checks_log_first(-10, "0001")
    last = db_get_checks_log_last(-10, "0001")

    assert first[0]["message_id"]['N'] == 231432
    assert last[0]["message_id"]['N'] == 457594

    first = db_get_checks_log_first(-11, "0002")
    last = db_get_checks_log_last(-11, "0001")

    assert first[0]["message_id"]['N'] == 656345
    assert last[0]["message_id"]['N'] == 876657
