"""Any mocks"""


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
