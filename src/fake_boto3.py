
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

    def put_item(self, TableName, Item): # pylint: disable=C0103
        """Put item to db"""
        return Item, TableName

    def get_item(self, TableName, Key): # pylint: disable=C0103
        """Get item from db"""
        return TableName, Key

    def scan(self,
        TableName, FilterExpression, # pylint: disable=C0103
        ExpressionAttributeNames, ExpressionAttributeValues ): # pylint: disable=C0103
        """Search items in db"""
        return TableName, FilterExpression, ExpressionAttributeNames, ExpressionAttributeValues


def client(client_name):
    """Return """
    if client_name == "kms":
        return KMS()

    if client_name == "dynamodb":
        return DynamoDB()

    return None
