"""Test Vectra authentication"""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use
import os
from azure.identity import DefaultAzureCredential
from ...vectra import VectraClient


class TestVectraAPI:
    """ Class for testing Vectra authentication """

    def test_vectra_api(self):
        """ Test the get_host method """
        base_url = os.getenv('VECTRA_API_URL')
        print(base_url)
        vectra_client = VectraClient(base_url, DefaultAzureCredential())
        assert vectra_client # nosec B101
