"""Test Vectra detections"""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use, duplicate-code
import os
from azure.identity import DefaultAzureCredential
from ...vectra import VectraClient


class TestDetection:
    """ Class for testing detection functions """

    def test_get_detection(self):
        """ Test the get_detection method """
        base_url = os.getenv('VECTRA_API_URL')
        vectra_client = VectraClient(base_url, DefaultAzureCredential())
        stakeholder = os.getenv('TEST_STAKEHOLDER')
        detection_id = os.getenv('TEST_DETECTION_ID')
        detection_info = vectra_client.get_detection(stakeholder, detection_id)
        assert detection_info['id'] # nosec B101
