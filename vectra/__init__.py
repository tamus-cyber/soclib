"""Main file for Vectra API Python wrapper."""

from typing import Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from azure.identity import EnvironmentCredential, DefaultAzureCredential


class VectraClient:
    """ Client for interacting with SOC Vectra API

    Attributes:
        base_url (str): Base URL for the API
        credential (Union[EnvironmentCredential, DefaultAzureCredential]):
            Azure credential object for authentication
        http_adapter (HTTPAdapter, optional):
            HTTP adapter to use for requests. Defaults to None.
    """

    def __init__(self, base_url: str, credential: Union[EnvironmentCredential, \
            DefaultAzureCredential], http_adapter: HTTPAdapter = None):
        """Initialize the client object."""
        self.base_url = base_url
        self.credential = credential
        self.http_adapter = http_adapter or HTTPAdapter(
            max_retries=Retry(total=3, backoff_factor=1))
        result = credential.get_token(f'{base_url}/.default')
        session = requests.Session()
        session.headers['Authorization'] = f'Bearer {result.token}'
        session.mount('https://', self.http_adapter)
        self.session = session

    def get_detection(self, stakeholder: str, detection_id: str):
        """ Get detection information from Vectra for a given detection ID
        Args:
            stakeholder (str): Stakeholder name
            detection_id (str): Detection ID
        Returns:
            dict: Detection information
        """
        # Fetch the detection information from Vectra API
        # Init an empty dictionary for when we handle account based detections in the future.
        detection_info = {}
        detection_info = self.session.get(
            f'{self.base_url}/detection/{stakeholder}/{detection_id}').json()
        return detection_info

    def get_host(self, stakeholder: str, host_id: str):
        """ Get host information from Vectra for a given host ID
        Args:
            stakeholder (str): Stakeholder name
            host_id (str): Host ID
        Returns:
            dict: Host information
        """
        # Fetch the host information from Vectra API
        host_info = {}
        host_info = self.session.get(
            f'{self.base_url}/host/{stakeholder}/{host_id}').json()
        return host_info

    def add_detection_tag(self, stakeholder: str, detection_id: str, tag: str):
        """ Add a tag to a detection
        Args:
            stakeholder (str): Stakeholder name
            detection_id (str): Detection ID
            tag (str): Tag to add
        Returns:
            dict: Response from Vectra API
        """
        # Add a tag to a detection
        response = self.session.post(
            f'{self.base_url}/detection/{stakeholder}/{detection_id}/tags', json={'tag': tag})
        return response.json()

    def add_detection_note(self, stakeholder: str, detection_id: str, note: str):
        """ Add a note to a detection
        Args:
            stakeholder (str): Stakeholder name
            detection_id (str): Detection ID
            note (str): Note to add
        Returns:
            dict: Response from Vectra API
        """
        # Add a note to a detection
        response = self.session.post(
            f'https://app-vectra-api.azurewebsites.net/detection/\
                {stakeholder}/{detection_id}/notes', json={'note': note})
        return response.json()
