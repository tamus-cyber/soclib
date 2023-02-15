# pylint: disable=line-too-long
"""Client for interacting with SOC Vectra API"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from azure.identity import EnvironmentCredential, DefaultAzureCredential

from loguru import logger
logger.disable(__name__)


class VectraClient:
    """ Client for interacting with SOC Vectra API"""

    def __init__(self, base_url: str, credential: EnvironmentCredential | DefaultAzureCredential,
                    http_adapter: HTTPAdapter = None):
        """Initialize the client object.

        Args:
            base_url (str): Base URL for the API
            credential (Union[EnvironmentCredential, DefaultAzureCredential]):
                Azure credential object for authentication
            http_adapter (HTTPAdapter, optional):
                HTTP adapter to use for requests. Defaults to None.
        """
        logger.debug('Initializing VectraClient')
        self.base_url = base_url
        self.credential = credential
        self.http_adapter = http_adapter or HTTPAdapter(
            max_retries=Retry(total=3, backoff_factor=1))
        result = credential.get_token(f'{base_url}/.default')
        session = requests.Session()
        session.headers['Authorization'] = f'Bearer {result.token}'
        # Add the reauth hook and the raise_for_status hook
        session.mount('https://', self.http_adapter)
        self.session = session

    def _refresh_session_token(self):
        """ Refresh the token in the session """
        result = self.credential.get_token(f'{self.base_url}/.default')
        self.session.headers['Authorization'] = f'Bearer {result.token}'

    def _request(self, method: str, url: str, **kwargs):
        """Wrapper for HTTP requests to handle exceptions and logging

        Args:
            method (str): HTTP method to use
            url (str): URL to make request to
            **kwargs: Additional arguments to pass to requests
        """
        try:
            response = self.session.request(method, url, **kwargs)

            # If we get a 401, try to update the token and retry the request
            if response.status_code == 401:
                logger.warning(
                    'HTTP 401 response. Attempting to get new token...')
                self._refresh_session_token()
                response = self.session.request(method, url, **kwargs)

            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            # If we get another 401, reauth failed, don't retry
            if response.status_code == 401:
                logger.error(
                    'New JWT invalid. Unable to get new, valid token.')
                raise err
            logger.warning(f'Bad response (HTTP {err.response.status_code}) from Vectra API: {err.response.text}')
            raise err
        except requests.exceptions.ConnectionError as err:
            logger.warning(f'Unable to connect to Vectra API: {err}')
            raise err
        except requests.exceptions.ReadTimeout as err:
            logger.warning(f'Read timeout for Vectra API: {err}')
            raise err

    def _get(self, url, **kwargs):
        """ Wrapper for GET requests """
        return self._request('GET', url, **kwargs)

    def _post(self, url, **kwargs):
        """ Wrapper for POST requests """
        return self._request('POST', url, **kwargs)

    def _put(self, url, **kwargs):
        """ Wrapper for PUT requests """
        return self._request('PUT', url, **kwargs)

    def _delete(self, url, **kwargs):
        """ Wrapper for DELETE requests """
        return self._request('DELETE', url, **kwargs)

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
        # detection_info = self.session.get(
        #     f'{self.base_url}/detection/{stakeholder}/{detection_id}').json()
        detection_info = self._get(
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
        host_info = self._get(
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
        response = self._post(
            f'{self.base_url}/detection/{stakeholder}/{detection_id}/tags', json={'tag': tag})
        return response.json()

    def get_detection_tag(self, stakeholder: str, detection_id: str):
        """ Get tags for a detection

        Args:
            stakeholder (str): Stakeholder name
            detection_id (str): Detection ID

        Returns:
            dict: Response from Vectra API
        """
        # Get tags for a detection
        response = self._get(
            f'{self.base_url}/detection/{stakeholder}/{detection_id}/tags')
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
        response = self._post(
            f'{self.base_url}/detection/\
                {stakeholder}/{detection_id}/notes', json={'note': note})
        return response.json()

    def get_pcap(self, stakeholder: str, detection_id: str):
        """ Get PCAP for a detection

        Args:
            stakeholder (str): Stakeholder name
            detection_id (str): Detection ID

        Returns:
            dict: Response from Vectra API
        """
        # Get PCAP for a detection
        response = self._get(
            f'{self.base_url}/detection/{stakeholder}/{detection_id}/pcap')
        return response.json()

    def get_health(self, stakeholder: str):
        """ Get health information for a stakeholder

        Args:
            stakeholder (str): Stakeholder name

        Returns:
            dict: Response from Vectra API
        """
        # Get health information for a stakeholder
        response = self._get(
            f'{self.base_url}/health/{stakeholder}')
        return response.json()

    def get_threat_feeds(self, stakeholder: str):
        """ Get threat feeds for a stakeholder

        Args:
            stakeholder (str): Stakeholder name

        Returns:
            dict: Response from Vectra API
        """
        # Get threat feeds for a stakeholder
        response = self._get(
            f'{self.base_url}/threatFeeds/{stakeholder}')
        return response.json()

    def add_threat_feed(self, stakeholder: str, threat_feed: dict):
        """ Add a threat feed for a stakeholder

        Args:
            stakeholder (str): Stakeholder name
            threat_feed (dict): Threat feed to add
                Example:
                {
                    "name": "SOC-INT-Threat-Feed-1",
                    "certainty": "High",
                    "indicator_type": "Watchlist",
                    "category": "cnc"
                }

        Returns:
            dict: Response from Vectra API
        """
        # Add a threat feed for a stakeholder
        response = self._post(
            f'{self.base_url}/threatFeeds/{stakeholder}', json=threat_feed)
        return response.json()

    def delete_threat_feed(self, stakeholder: str, threat_feed_id: str):
        """ Delete a threat feed for a stakeholder

        Args:
            stakeholder (str): Stakeholder name
            threat_feed_id (str): Threat feed ID

        Returns:
            dict: Response from Vectra API
        """
        # Delete a threat feed for a stakeholder
        response = self._delete(
            f'{self.base_url}/threatFeeds/{stakeholder}/{threat_feed_id}')
        return response.json()

    def get_users(self, stakeholder: str):
        """ Get users for a stakeholder

        Args:
            stakeholder (str): Stakeholder name

        Returns:
            list: Response from Vectra API

        Example:
            .. code-block:: json

                [
                    {
                        "id": 20,
                        "username": "admin",
                        "lastLogin": "2021-12-01T23:16:18Z",
                        "role": {
                            "id": 3,
                            "name": "Super Admin"
                        },
                        "currentUser": false,
                        "APIToken": "",
                        "userType": "local"
                    }
                ]
            ::
        """
        # Get users for a stakeholder
        response = self._get(
            f'{self.base_url}/users/{stakeholder}')
        return response.json()

    def search(self, stakeholder: str, search_type: str, query: str):
        """ Search for a given query

        Args:
            stakeholder (str): Stakeholder name
            search_type (str): Type of search to perform
                Options: accounts, hosts, detections
            query (str): Query to search for
                Example: "detection.src_ip: ...

        Returns:
            dict: Response from Vectra API
        """
        # Search for a given query
        response = self._get(
            f'{self.base_url}/search/{stakeholder}/?type={search_type}&query={query}')
        return response.json()

    def refresh_syslog(self, stakeholder: str):
        """ Refresh syslog configuration

        Args:
            stakeholder (str): Stakeholder name

        Returns:
            dict: Response from Vectra API
        """
        # Refresh syslog configuration
        response = self._post(
            f'{self.base_url}/syslog/{stakeholder}/refresh')
        return response.json()
