"""Test Umbrella API."""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use, line-too-long
import os
from ...reputation.umbrella import UmbrellaClient


class TestUmbrellaAPI:
    """ Class for testing the Umbrella API """

    def test_umbrella_init(self):
        """Test Umbrella API initialization."""
        api_key = os.getenv("UMBRELLA_API_KEY")
        umbrella_client = UmbrellaClient(api_key)
        assert isinstance(umbrella_client, UmbrellaClient) # nosec B101

    def test_umbrella_get_domain_category(self):
        """Test Umbrella API get_domain_category."""
        api_key = os.getenv("UMBRELLA_API_KEY")
        umbrella_client = UmbrellaClient(api_key)
        domain = "google.com"
        assert "Search Engines" in umbrella_client.get_domain_category(domain).get("categories") # nosec B101

    def test_umbrella_get_asn(self):
        """Test Umbrella API get_asn."""
        api_key = os.getenv("UMBRELLA_API_KEY")
        umbrella_client = UmbrellaClient(api_key)
        ip_address = "1.1.1.1"
        assert umbrella_client.get_asn(ip_address)[0].get("asn") == 13335 # nosec B101
