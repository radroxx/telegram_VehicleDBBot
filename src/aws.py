"""AWS Clients"""

import os
import base64
import boto3 # pylint: disable=E0401
from .cache import cache_exists, cache_read, cache_write


def aws_kms():
    """Get aws kms client"""

    if cache_exists("aws_client_kms") is False:
        client = boto3.client('kms')
        cache_write("aws_client_kms", client)
    return cache_read("aws_client_kms")


def aws_dynamodb():
    """Get aws dynamodb client"""

    if cache_exists("aws_client_dynamodb") is False:
        client = boto3.client('dynamodb')
        cache_write("aws_client_dynamodb", client)
    return cache_read("aws_client_dynamodb")


def aws_kms_decrypt(data_in_base64):
    """Decrypt data"""

    client = aws_kms()

    return client.decrypt(
        CiphertextBlob=base64.b64decode(data_in_base64),
        EncryptionContext={'LambdaFunctionName': os.getenv("AWS_LAMBDA_FUNCTION_NAME", "")}
    )['Plaintext'].decode('utf-8')
