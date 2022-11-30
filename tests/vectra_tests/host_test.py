"""Test Vectra hosts"""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use
import sys
import os
from azure.identity import DefaultAzureCredential
sys.path.append('..') # Import parent directory
from dotenv import load_dotenv
from soclib.vectra import VectraClient

load_dotenv()

class TestHost:
    """ Class for testing host functions """

    def test_get_host(self):
        """ Test the get_host method """
        base_url = os.getenv('BASE_URL')
        vectra_client = VectraClient(base_url, DefaultAzureCredential())
        stakeholder = os.getenv('TEST_STAKEHOLDER')
        host_id = os.getenv('TEST_HOST_ID')
        host_info = vectra_client.get_host(stakeholder, host_id)
        assert host_info.get('id') # nosec B101
