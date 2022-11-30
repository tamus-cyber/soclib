"""Test Vectra detections"""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use
import sys
import json
from azure.identity import DefaultAzureCredential
sys.path.append('..') # Import parent directory
from soclib.vectra import VectraClient

class TestDetection:
    """ Class for testing detection functions """

    def test_get_detection(self):
        """ Test the get_detection method """
        base_url = 'https://app-vectra-api.azurewebsites.net'
        vectra_client = VectraClient(base_url, DefaultAzureCredential())
        detection_info = vectra_client.get_detection('TAMUCC', '438882')
        with open('tests/input_data/detection.json', 'r', encoding='utf-8') as file:
            expected_detection_info = json.load(file)
        assert detection_info == expected_detection_info # nosec B101
