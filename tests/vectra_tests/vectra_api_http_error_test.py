"""Test Vectra HTTP error handling"""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use
import sys
import os
from azure.identity import DefaultAzureCredential
import requests
sys.path.append('..') # Import parent directory
from dotenv import load_dotenv
from soclib.vectra import VectraClient

load_dotenv()

class TestVectraAPIHTTPError:
    """ Class for testing Vectra HTTP error handling """

    def test_vectra_api_reauth(self):
        """ Test a 404 exception being raised """
        base_url = os.getenv('VECTRA_API_URL')

        # Do authentication
        vectra_client = VectraClient(base_url, DefaultAzureCredential())
        
        # Do get_detection with fake stakeholder and detection ID
        status_code = 200
        try:
            vectra_client.get_detection("bad_stakeholder", "1")
        except requests.exceptions.HTTPError as err:
            status_code = err.response.status_code
        assert status_code == 404 # nosec B101
