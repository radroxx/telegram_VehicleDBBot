"""Test platerecognizer client"""

import os
import base64
import urllib3

from .test_mock import create_facke_boto3_module
from .cache import cache_wipe_key
from .platerecognizer import platerecognizer_plate_reader


create_facke_boto3_module()


def mock_request(status, body, func = None):
    """Mock request"""
    def request(self, method, url, fields=None, headers=None, **urlopen_kw): # pylint: disable=W0613
        if func:
            func(method, url, fields, headers, **urlopen_kw)
        response = type('', (), {})
        setattr(response, "status", status)
        setattr(response, "data", body)
        return response
    return request


def test_platerecognizer_plate_reader_headers():
    """Test platerecognizer"""

    test_data = base64.b64encode(b"Hello world 1").decode("UTF-8")
    os.environ["PLATERECOGNIZER_API"] = test_data
    cache_wipe_key("config_platerecognizer_api_key")

    def test_headers(method, url, fields, headers, **urlopen_kw): # pylint: disable=W0613
        assert "Authorization" in headers
        assert headers["Authorization"] == "Token Hello world 1"
        assert "upload_url" in fields
        assert "regions" in fields
        assert fields["upload_url"] == "https://example.org/plate_test.jpg"

    urllib3.PoolManager.request = mock_request(201, '{"results":[]}', test_headers)
    plates_data = platerecognizer_plate_reader("https://example.org/plate_test.jpg")
    assert 'results' in plates_data
