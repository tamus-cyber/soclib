"""Test Vectra authentication"""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use
import sys
import os
from azure.identity import DefaultAzureCredential
sys.path.append('..') # Import parent directory
from dotenv import load_dotenv
from soclib.vectra import VectraClient

load_dotenv()

class TestVectraAPI:
    """ Class for testing Vectra authentication """

    def test_vectra_api(self):
        """ Test the get_host method """
        base_url = os.getenv('VECTRA_API_URL')
        vectra_client = VectraClient(base_url, DefaultAzureCredential())
        assert vectra_client # nosec B101
