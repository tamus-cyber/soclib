import sys
import json
sys.path.append('..')
from soclib.vectra import VectraClient
from azure.identity import DefaultAzureCredential

class TestDetection:
    """ Class for testing detection functions """

    def test_get_detection(self):
        """ Test the get_detection method """
        base_url = 'https://app-vectra-api.azurewebsites.net'
        vectra_client = VectraClient(base_url, DefaultAzureCredential())
        detection_info = vectra_client.get_detection('TAMUCC', '438882')
        with open('tests/input_data/detection.json', 'r', encoding='utf-8') as f:
            expected_detection_info = json.load(f)
        assert detection_info == expected_detection_info
