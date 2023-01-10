"""platerecognizer client"""
import json
import urllib3
from .config import config_platerecognizer_api_key


def platerecognizer_plate_reader(file_url):
    """Detected plates number in photo"""

    with urllib3.PoolManager() as pool:
        response = pool.request(
            "POST", "https://api.platerecognizer.com/v1/plate-reader/",
            headers={'Authorization': 'Token ' + config_platerecognizer_api_key()},
            fields={
                'regions': 'lt',
                'upload_url': file_url
            }
        )
        data = json.loads(response.data) # pylint: disable=E1101
        if response.status in (200, 201) and data is not None: # pylint: disable=E1101
            return data
    return {"results": []}
