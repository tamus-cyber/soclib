# pylint: disable=broad-except, invalid-name, no-self-use
"""Main file for Umbrella API Python wrapper."""

import socket
import requests

UMBRELLA_URL = "https://investigate.api.umbrella.com"

class UmbrellaClient:
    """Class for interacting with the Umbrella API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.umbrella_session = get_umbrella_session(self.api_key)

    def get_domain_category(self, domain: str) -> dict:
        """
        Get the category of a domain.

        Args:
            domain (str): The domain to get the category of.

        Returns:
            dict: The category of the domain in the following format:
                'categories': List of categories (list)
                'status': One of the following: [malicious, benign, unknown] (str)
        """
        url = f"{UMBRELLA_URL}/domains/categorization/{domain}?showLabels=true"
        response = self.umbrella_session.get(url)
        if response.status_code == 200:
            categories = []
            # If there is "content_categories" or "security_categories" in the response,
            # add them to the list of categories.
            if "content_categories" in response.json()[domain]:
                categories.extend(
                    response.json()[domain]["content_categories"])
            if "security_categories" in response.json()[domain]:
                categories.extend(
                    response.json()[domain]["security_categories"])

            # If the domain is considered malicious, the status returned is -1.
            # If the domain is considered benign, the status returned is 1.
            # If the domain is unclassified, the status returned is 0.
            status = response.json()[domain]["status"]
            status_map = {-1: "malicious", 1: "benign", 0: "unclassified"}
            status = status_map[status]

            return {"status": status, "categories": categories}
        return {"status": 0, "categories": []}

    def resolve_domain(self, domain: str) -> str:
        """
        Resolve a domain to an IP address.

        Args
            domain (str): The domain to resolve.

        Returns
            str: The IP address of the domain.
        """
        ip = socket.gethostbyname(domain)
        return ip

    def get_asn(self, ip: str) -> dict:
        """
        Get the ASN of an IP address

        Args:
            ip (str): The IP address to get the ASN of.

        Returns:
            dict: The ASN of the IP address in the following format:
                'asn': The ASN of the IP address (str)
                'cidr': The CIDR of the IP address (str)
                'ir': The IR of the IP address (str)
                'description': The description of the IP address (str)
                'creation_date': The date the IP address was created (str)
        """
        url = f"{UMBRELLA_URL}/bgp_routes/ip/{ip}/as_for_ip.json"
        response = self.umbrella_session.get(url)
        if response.status_code == 200:
            return response.json()
        return None

def get_umbrella_session(api_key: str) -> requests.sessions.Session:
    """ Create a session for interacting with the Umbrella API.

    Args:
        api_key (str): The API key to use for the session.

    Returns:
        requests.sessions.Session: The session to use for interacting with the Umbrella API.
    """
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    })

    return session
