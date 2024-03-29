"""Test Vectra reauth failure handling"""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use
import os
import requests
from azure.identity import DefaultAzureCredential
from ...vectra import VectraClient


class BadCredential(DefaultAzureCredential):
    """ Class to hijack the DefaultAzureCredential """

    def __init__(self, *args, **kwargs):
        self.token_calls = 0
        super().__init__(*args, **kwargs)

    def get_token(self, *args, **kwargs):  # pylint: disable=unused-argument
        """ Return a bad token """
        # make an instance of an object with a token attribute
        class BadAccessToken:
            """ Defines an object with a token attribute to mimic the AccessToken object """
            token = 'BrokenMcTokenFace'
        result = BadAccessToken()
        self.token_calls += 1
        return result


class TestVectraAPINoReauthLoop:
    """ Class for testing Vectra re-authentication """

    def test_vectra_api_no_reauth_loop(self):
        """ Test the 401 reauth functionality """
        base_url = os.getenv('VECTRA_API_URL')

        # initialize the client with a credential that will never work
        vectra_client = VectraClient(base_url, BadCredential())

        # # Do get_detection with bad auth
        stakeholder = os.getenv('TEST_STAKEHOLDER')
        detection_id = os.getenv('TEST_DETECTION_ID')

        recieved_401_error = False
        try:
            vectra_client.get_detection(stakeholder, detection_id)
        except requests.exceptions.HTTPError:
            recieved_401_error = True

        token_calls = vectra_client.credential.token_calls
        assert recieved_401_error
        assert token_calls == 2
