"""Test OTX API."""
# pylint: disable=wrong-import-position, import-error, too-few-public-methods, no-self-use
import os
from ...reputation.otx import AlienVaultOTXClient


class TestOTXAPI:
    """ Class for testing the OTX API """

    def test_otx_init(self):
        """Test OTX API initialization."""
        api_key = os.getenv("OTX_API_KEY")
        otx_client = AlienVaultOTXClient(api_key)
        assert isinstance(otx_client, AlienVaultOTXClient) # nosec B101

    def test_otx_get_whitelisted_domain(self):
        """Test OTX API get_whitelisted_domain."""
        api_key = os.getenv("OTX_API_KEY")
        otx_client = AlienVaultOTXClient(api_key)
        domain = "google.com"
        assert otx_client.get_whitelisted(domain) == True # nosec B101

    def test_otx_get_malware_families(self):
        """Test OTX API get_malware_families."""
        api_key = os.getenv("OTX_API_KEY")
        otx_client = AlienVaultOTXClient(api_key)
        malicious_domain = "krestinaful.com"
        malware_families = otx_client.get_malware_families(malicious_domain)
        assert "Chromeloader" in malware_families # nosec B101

    def test_otx_get_official_pulses(self):
        """Test OTX API get_official_pulses."""
        api_key = os.getenv("OTX_API_KEY")
        otx_client = AlienVaultOTXClient(api_key)
        malicious_domain = "krestinaful.com"
        pulses = otx_client.get_official_pulses(malicious_domain)
        assert "TLP" in pulses[0] # nosec B101