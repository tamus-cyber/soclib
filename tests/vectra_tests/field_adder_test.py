"""Test Vectra detections"""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use
import os
from azure.identity import DefaultAzureCredential
from ...vectra import VectraClient, add_extra_fields


class TestFieldAdd:
    """ Class for testing detection functions """

    def test_field_add(self):
        """ Test the get_detection method """
        base_url = os.getenv('VECTRA_API_URL')
        vectra_client = VectraClient(base_url, DefaultAzureCredential())
        stakeholder = os.getenv('TEST_STAKEHOLDER')
        detection_id = os.getenv('TEST_DETECTION_ID')
        detection_info = vectra_client.get_detection(stakeholder, detection_id)
        detection_info = add_extra_fields(detection_info, {'stakeholder': stakeholder})
        assert detection_info['stakeholder'] == stakeholder # nosec B101
