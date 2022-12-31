# pylint: disable=line-too-long
"""Main file for Vectra API Python wrapper."""

from typing import Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from azure.identity import EnvironmentCredential, DefaultAzureCredential
from ..custom_errors import DetectionNotFound


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
        # Add the reauth hook and the raise_for_status hook
        session.hooks['response'].extend([self._reauth_on_401, self._raise_for_status])
        session.mount('https://', self.http_adapter)
        self.session = session

    def _raise_for_status(self, response: requests.Response, *args, **kwargs):  # pylint: disable=unused-argument, no-self-use
        """ Raise an exception if the response status is not 200
        Args:
            response (requests.Response): Response object
        """
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404: # pylint: disable=no-else-raise
                raise DetectionNotFound from err
            else:
                raise err

    def _reauth_on_401(self, response: requests.Response, *args, **kwargs):  # pylint: disable=unused-argument
        """ Reauth hook for requests
        Args:
            response (requests.Response): Response object
        Returns:
            requests.Response: Response object
        """
        if response.status_code == 401:  # 401 is the status code for unauthorized
            result = self.credential.get_token(
                f'{self.base_url}/.default')  # Get a new token
            # Update the token in the session
            self.session.headers['Authorization'] = f'Bearer {result.token}'

            # grab the request that failed, update the token
            request = response.request
            request.headers['Authorization'] = f'Bearer {result.token}'

            # remove the reauth hook to prevent infinite loop if auth fails again
            # handle cases where the hooks['response'] is a single hook or a list of hooks
            if isinstance(request.hooks['response'], list):
                request.hooks['response'].remove(self._reauth_on_401)
            else:
                # if there is only one hook, it has to be this on. Set it to None
                request.hooks['response'] = None

            # retry the request
            response = self.session.send(request)
        return response

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

    def get_detection_tag(self, stakeholder: str, detection_id: str):
        """ Get tags for a detection
        Args:
            stakeholder (str): Stakeholder name
            detection_id (str): Detection ID
        Returns:
            dict: Response from Vectra API
        """
        # Get tags for a detection
        response = self.session.get(
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
        response = self.session.post(
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
        response = self.session.get(
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
        response = self.session.get(
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
        response = self.session.get(
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
        response = self.session.post(
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
        response = self.session.delete(
            f'{self.base_url}/threatFeeds/{stakeholder}/{threat_feed_id}')
        return response.json()

    def get_users(self, stakeholder: str):
        """ Get users for a stakeholder
        Args:
            stakeholder (str): Stakeholder name
        Returns:
            dict: Response from Vectra API
                Example:
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
        """
        # Get users for a stakeholder
        response = self.session.get(
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
        response = self.session.get(
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
        response = self.session.post(
            f'{self.base_url}/syslog/{stakeholder}/refresh')
        return response.json()

# Utility functions
def get_dst_ips(detection: dict) -> set:
    """Get destination IPs from a Vectra detection.

    Args:
        detection (dict): Vectra detection JSON dictionary.

    Returns:
        set: Set of destination IPs.
    """
    dst_ips = set()

    for group in detection['grouped_details']:
        # Most detections put destination IPs in the 'dst_ips' key.
        dst_ips.update(group.get('dst_ips', []))
        # Multi-home Fronted Tunnel puts destination IPs in the 'cdn_ips' key.
        dst_ips.update(group.get('cdn_ips', []))
        # I honestly can't remember which detection type does this...
        dst_ips.update([dc['ip'] for dc in group.get('domain_controllers', {})])

    return dst_ips


def get_dst_subnets(detection: dict) -> set:
    """Get destination subnets from a Vectra detection.

    Args:
        detection (dict): Vectra detection JSON dictionary.

    Returns:
        set: Set of destination subnets.
    """
    dst_subnets = set()

    for group in detection['grouped_details']:
        dst_subnets.update(group.get('dst_subnets', []))

    return dst_subnets


def get_dst_ports(detection: dict) -> set:
    """Get destination ports from a Vectra detection.

    Args:
        detection (dict): Vectra detection JSON dictionary.

    Returns:
        set: Set of destination ports.
    """
    dst_ports = set()

    for group in detection['grouped_details']:
        dst_ports.update(group.get('dst_ports', []))

    return dst_ports


def get_target_domains(detection: dict, dst_ips: set) -> set:
    """Get target domains from a Vectra detection.

    Args:
        detection (dict): Vectra detection JSON dictionary.
        dst_ips (set): Set of destination IPs.

    Returns:
        set: Set of target domains.
    """

    target_domains = set()

    for group in detection['grouped_details']:
        # We don't want to add a "target domain" if that "domain" is just destination IP since Vectra does that sometimes. :/
        # We also check that the domain isn't just an empty string since sometimes that is what Vectra gives us...
        if isinstance(group.get('target_domains'), list):  # Sometimes the target_domains key exists but the value is None.
            target_domains.update([domain.lower() for domain in group.get('target_domains', []) if domain not in dst_ips and domain])  # Force all domains to lower case
        elif isinstance(group.get('target_domains'), str):  # In Cognito 6.4, sometimes the type is str and sometimes is list :head-desk:
            target_domains.add(group['target_domains'])

        # Some detection types (like Automated Replication) have destination hostnames under ['grouped_details'][n]['dst_hosts'][n]['name'].
        # With 6.2, some detection types return 'dst_hosts' as dictionary and not a list - like every other detection type.
        if isinstance(group.get('dst_hosts'), dict):
            if 'name' in group.get('dst_hosts'):
                if group['dst_hosts']['name']:  # See if it is empty string or not.
                    target_domains.add(group['dst_hosts']['name'].lower())
        elif isinstance(group.get('dst_hosts'), list):
            # Sometimes Vectra Threat Intelligence Match detection types have the target domain in ['dst_hosts'][n]['dst_dns'].
            # Unforunately, the 'name' key is the DNS server that resolved the domain, not the domain itself.
            if detection['detection_type'] == 'Vectra Threat Intelligence Match':
                for host in group['dst_hosts']:
                    if host.get('dst_dns'):  # Sometime it can just be an empty string
                        target_domains.add(host['dst_dns'])
            # Every other detection type has the target domain in ['dst_hosts'][n]['name'].
            else:
                target_domains.update([host.get('name', '').lower() for host in group.get('dst_hosts', []) if host.get('name')])  # Again, always lower case.

    return target_domains


def get_dns_responses(detection: dict) -> set:
    """Get DNS responses from a Vectra detection.

    Args:
        detection (dict): Vectra detection JSON dictionary.

    Returns:
        set: Set of DNS responses.
    """
    dns_responses = set()

    for group in detection['grouped_details']:
        if 'dns_response' in group:
            if isinstance(group['dns_response'], str):
                dns_responses.update(group['dns_response'].split(','))
            elif isinstance(group['dns_response'], list):
                dns_responses.update(group['dns_response'])
        # Threat intelligence detections store DNS responses in a different place...
        if detection['detection_type'].endswith('Threat Intelligence Match') and group['primary_match'] == 'dns_request':
            for event in group['connection_events']:
                dns_responses.update(event['dns_resolved_ips'])

    return dns_responses


def add_extra_fields(detection: dict, extra_fields: dict) -> dict:
    """Add extra fields to a Vectra detection.

    Args:
        detection (dict): Vectra detection JSON dictionary.
        extra_fields (dict): Extra fields to add to the detection.

    Returns:
        dict: Vectra detection JSON dictionary with extra fields added.
    """
    for key, value in extra_fields.items():
        if key not in detection:
            detection[key] = value
        else:
            raise ValueError(f'Extra field "{key}" already exists in detection (value: {detection[key]}).')
    return detection
