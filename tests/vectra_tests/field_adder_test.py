"""Test Vectra detections"""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use
import sys
import os
from azure.identity import DefaultAzureCredential
sys.path.append('..') # Import parent directory
from dotenv import load_dotenv
from soclib.vectra import VectraClient, add_extra_fields

load_dotenv()

class TestFieldAdd:
    """ Class for testing detection functions """

    def test_field_add(self):
        """ Test the get_detection method """
        base_url = os.getenv('BASE_URL')
        vectra_client = VectraClient(base_url, DefaultAzureCredential())
        stakeholder = os.getenv('TEST_STAKEHOLDER')
        detection_id = os.getenv('TEST_DETECTION_ID')
        detection_info = vectra_client.get_detection(stakeholder, detection_id)
        detection_info = add_extra_fields(detection_info, {'stakeholder': stakeholder})
        assert detection_info['stakeholder'] == stakeholder # nosec B101