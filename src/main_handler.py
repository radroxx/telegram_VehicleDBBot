"""Main handler"""

def handler(event, context):
    """Handler"""

    if event is None and context is None:
        return {"statusCode": 200, "body": "True"}

    return {"statusCode": 200, "body": "True"}
