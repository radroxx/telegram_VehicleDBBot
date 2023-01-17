"""Test aws"""

import base64
from boto3 import DynamoDB, KMS
from .cache import cache_init
from .aws import aws_kms, aws_dynamodb, aws_kms_decrypt # pylint: disable=C0413


def setup_module(module): # pylint: disable=W0613
    """Init"""
    cache_init()


def test_kms():
    """Test aws kms cache"""
    kms_one = aws_kms()
    kms_two = aws_kms()

    assert id(kms_one) == id(kms_two)
    assert isinstance(kms_one, KMS)


def test_dynamodb():
    """Test aws dynamodb cache"""
    dynamodb_one = aws_dynamodb()
    dynamodb_two = aws_dynamodb()
    assert id(dynamodb_one) == id(dynamodb_two)
    assert isinstance(dynamodb_one, DynamoDB)


def test_kms_decrypt():
    """Test decrypt method"""

    test_data = base64.b64encode(b"Hello world")
    assert aws_kms_decrypt(test_data) == "Hello world"


def test_kms_decrypt_count():
    """Test decrypt count method call"""

    test_data = base64.b64encode(b"Hello world")
    d_count = aws_kms().decrypt_count

    aws_kms_decrypt(test_data)
    aws_kms_decrypt(test_data)
    aws_kms_decrypt(test_data)

    assert aws_kms().decrypt_count - d_count == 3
