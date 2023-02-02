"""Test TimeoutHTTPAdapter"""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use
import requests
from ...timeout_adapter import TimeoutHTTPAdapter


class TestTimeout:
    """ Class for testing TimeoutHTTPAdapter """

    def test_azure_login(self):
        """ Test the timeout adapter """
        base_url = "https://www.google.com"
        session = requests.Session()
        session.mount(base_url, TimeoutHTTPAdapter(timeout=1))
        response = session.get(base_url)
        assert response.status_code == 200 # nosec B101
