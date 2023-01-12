"""Fuck boto3 module"""

_database = {}

class KMS: # pylint: disable=R0903
    """Mock aws kms encrypt"""

    def __init__(self) -> None:
        self.decrypt_count = 0

    def decrypt(self, CiphertextBlob, EncryptionContext): # pylint: disable=C0103,W0613
        """Mock decrypt data, return unmodify CiphertextBlob"""
        self.decrypt_count += 1
        return {"Plaintext": CiphertextBlob}


class DynamoDB:
    """Mock aws dynamodb"""

    def __init__(self) -> None:
        self._tables = {}

    def list_tables(self):
        """Return empty tables list"""
        return {"TableNames": []}

    def create_table(self, *args, **kwargs):
        """Create table"""
        raise NotImplementedError()

    def put_item(self, TableName, Item): # pylint: disable=C0103
        """Put item to db"""
        if TableName not in _database:
            _database[TableName] = []

        if Item in _database[TableName]:
            return

        _database[TableName].append(Item)

    def get_item(self, TableName, Key): # pylint: disable=C0103
        """Get item from db"""

        #print(TableName, Key)
        for item in _database.get(TableName, []):
            is_complies_with_rules = True
            for rule in Key.keys():
                #print(rule, list(Key[rule].values())[0], "==", list(item[rule].values())[0])
                if list(Key[rule].values())[0] != list(item[rule].values())[0]:
                    is_complies_with_rules = False
                    break
            if is_complies_with_rules:
                return {"Item": item}
        return {}

    def query(self, *, TableName, IndexName = None,
        KeyConditionExpression, FilterExpression = None, ExpressionAttributeNames, # pylint: disable=W0613
        ExpressionAttributeValues, ScanIndexForward, Limit):
        """Search items in db"""
        responce = []

        order_by = "timestamp"
        if IndexName == "user_raiting":
            TableName = "vehicledbbot_users"
            order_by = "raiting"
        if IndexName == "vehicle_raiting":
            TableName = "vehicledbbot_vehicles_rating"
            order_by = "raiting"

        for item in _database[TableName]:
            if item["chat_id"]['N'] != ExpressionAttributeValues[":chat_id"]['N']:
                continue
            if TableName == "vehicledbbot_check_logs" and \
                item["plate"]['S'] != ExpressionAttributeValues[":plate"]['S']:
                continue
            responce.append(item)

        ordered_list = sorted(
            responce,
            key=lambda k: int(k[order_by]['N']),
            reverse=ScanIndexForward
        )

        return {"Items": ordered_list[0:Limit]}


def client(client_name):
    """Return """
    if client_name == "kms":
        return KMS()

    if client_name == "dynamodb":
        return DynamoDB()

    return None
