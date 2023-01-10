"""Test platerecognizer client"""

import os
import base64
import urllib3

from .test_mock import mock_request
from .cache import cache_wipe_key
from .platerecognizer import platerecognizer_plate_reader


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

    old_request = urllib3.PoolManager.request
    urllib3.PoolManager.request = mock_request(201, '{"results":[]}', test_headers)
    plates_data = platerecognizer_plate_reader("https://example.org/plate_test.jpg")
    urllib3.PoolManager.request = old_request
    assert 'results' in plates_data
