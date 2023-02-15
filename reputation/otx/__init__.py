"""Main file for AlienVault OTX API Python wrapper."""

import requests
from requests.adapters import HTTPAdapter

OTX_URL = "https://otx.alienvault.com/api/v1/indicators"


class AlienVaultOTXClient:
    """Class for interacting with the AlienVault OTX API."""

    def __init__(self, api_key: str, http_adapter: HTTPAdapter = None):
        """Initialize the AlienVaultOTXClient.

        Args:
            api_key (str): The OTX API key to use for the session.
            http_adapter (HTTPAdapter, optional): The HTTPAdapter to use for
                the session. Defaults to None.
        """
        self.api_key = api_key
        self.otx_session = requests.Session()
        self.otx_session.headers.update({
            "X-OTX-API-KEY": api_key
        })
        if http_adapter:
            self.otx_session.mount("https://", http_adapter)

    def get_whitelisted(self, domain: str) -> bool:
        """
        Check if a domain is on the OTX whitelist.

        Args:
            domain (str): The domain to get the category of.

        Returns:
            bool: True if the domain is on the whitelist, False otherwise
        """
        url = f"{OTX_URL}/domain/{domain}"
        response = self.otx_session.get(url)
        if response.status_code == 200:
            is_whitelisted = False
            if len(response.json()["validation"]) > 0:
                is_whitelisted = True
            return is_whitelisted
        return False

    def get_official_pulses(self, domain: str) -> list:
        """
        Get the official pulses of a domain. Used for threat intelligence.

        Args:
            domain (str): The domain to get the category of.

        Returns:
            list: List of official pulses
        """
        url = f"{OTX_URL}/domain/{domain}/general"
        response = self.otx_session.get(url)
        if response.status_code == 200:
            official_pulses = []
            for pulse in response.json()["pulse_info"]["pulses"]:
                if pulse["author"]["username"] == "AlienVault":
                    official_pulses.append(pulse)
            return official_pulses
        return []

    def get_malware_families(self, domain: str) -> list:
        """
        Get the malware families of a domain. Used for threat intelligence.

        Args:
            domain (str): The domain to get the category of.

        Returns:
            list: List of malware families
        """
        url = f"{OTX_URL}/domain/{domain}/general"
        response = self.otx_session.get(url)
        if response.status_code == 200:
            malware_families = []
            for malware in response.json()["pulse_info"]["related"]\
                ["alienvault"]["malware_families"]:
                malware_families.append(malware)
            return malware_families
        return []
