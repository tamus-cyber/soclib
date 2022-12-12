"""Test Vectra authentication"""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use
import sys
import os
from azure.identity import DefaultAzureCredential
sys.path.append('..') # Import parent directory
from dotenv import load_dotenv
from soclib.vectra import VectraClient

load_dotenv()

class TestVectraAPIReauth:
    """ Class for testing Vectra re-authentication """

    def test_vectra_api_reauth(self):
        """ Test the 401 reauth functionality """
        base_url = os.getenv('VECTRA_API_URL')

        # Do good auth
        vectra_client = VectraClient(base_url, DefaultAzureCredential())
        
        # Demolish the session token
        vectra_client.session.headers['Authorization'] = 'Bearer badtoken'
        badtoken = vectra_client.session.headers['Authorization']
        
        # Do get_detection with bad auth
        stakeholder = os.getenv('TEST_STAKEHOLDER')
        detection_id = os.getenv('TEST_DETECTION_ID')
        vectra_client.get_detection(stakeholder, detection_id)
        
        # Check that the token has changed
        new_token = vectra_client.session.headers['Authorization']
        
        assert badtoken != new_token # nosec B101
