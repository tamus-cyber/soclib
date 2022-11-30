"""Test Azure authentication"""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use
import sys
import os
from azure.identity import DefaultAzureCredential
sys.path.append('..') # Import parent directory
from dotenv import load_dotenv

load_dotenv()

class TestAzure:
    """ Class for testing Azure auth """

    def test_azure_login(self):
        """ Test the DefaultAzureCredential method """
        credential = DefaultAzureCredential()
        assert credential # nosec B101
