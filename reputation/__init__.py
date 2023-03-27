# pylint: disable-all
#!/usr/bin/env python3
from ipaddress import ip_address
from .otx import AlienVaultOTXClient
from .umbrella import UmbrellaClient
from ..geolocation import get_location_data
from ..misc import get_website_description

def enrich(indicator: str, otx_session: AlienVaultOTXClient, umbrella_session: UmbrellaClient, verbose=False) -> dict:
    """Manually enrich a single indicator

    Args:
        indicator (str): The indicator to enrich
        otx_session (AlienVaultOTXClient): The OTX session
        umbrella_session (UmbrellaClient): The Umbrella session
        verbose (bool, optional): Verbose output. Defaults to False.

    Returns:
        dict: The enriched indicator data
    """
    # Initialize the data dictionary
    data = {"indicator": indicator, "indicator_type": None, "ip_address": None, "otx": {}, "umbrella": {}}

    # Determine if the indicator is an IP or URL
    try: 
        ip_address(indicator)
        data["indicator_type"] = "ip"
        data["ip_address"] = indicator
        # Check if IP address is private
        if ip_address(indicator).is_private:
            return {"error": "Private IP address", "indicator": indicator}
    except ValueError:
        data["indicator_type"] = "domain"
        # We cannot do a DNS lookup because of new TLP: RED
        # and PAPP: RED indicators
        data["ip_address"] = None

    
    # Enrich the indicator
    # OTX
    print("Getting OTX data...", end=" ") if verbose else None
    try:
        data["otx"]['whitelisted'] = otx_session.get_whitelisted(indicator)
        data["otx"]['malware_families'] = otx_session.get_malware_families(indicator)
        temp_pulses = otx_session.get_official_pulses(indicator)
        # Prune the OTX pulses to only include the name, description, tags and references
        if len(temp_pulses) > 0:
            pulses = []
            for pulse in temp_pulses:
                pulses.append({
                    "name": pulse["name"],
                    "description": pulse["description"],
                    "tags": pulse["tags"],
                    "references": pulse["references"]
                })
            data["otx"]['official_pulses'] = pulses
        print("Done") if verbose else None
    except Exception as err:
        print(f"Failed ({err})") if verbose else None
        data["otx"] = {"error": f"Unable to get OTX data"}

    # Umbrella
    print("Getting Umbrella data...", end=" ") if verbose else None
    try:
        data["umbrella"]['categories'] = umbrella_session.get_domain_category(indicator)
        if data["ip_address"] is not None:
            data["umbrella"]['asn'] = umbrella_session.get_asn(data["ip_address"])
            passive_dns = umbrella_session.get_passive_dns(data["ip_address"])
            dns_records = []
            for record in passive_dns.get("records", []):
                domain = record.get("rr")
                if domain is not None:
                    dns_records.append(domain)
            data["umbrella"]['passive_dns'] = dns_records

        print("Done") if verbose else None
    except Exception as err:
        print(f"Failed ({err})") if verbose else None
        data["umbrella"] = {"error": f"Unable to get Umbrella data"}
    
    # Get geo location data (ipapi.co)
    print("Getting geolocation data...", end=" ") if verbose else None
    try:
        if data["ip_address"] is not None:
            # Check if IP address is private
            if ip_address(data["ip_address"]).is_private:
                data["geolocation"] = {"error": "Private IP address"}
            else:
                geo_data = get_location_data(data["ip_address"])
                temp = {}
                temp["country"] = geo_data.get("country_name", "Unknown")
                temp["region"] = geo_data.get("region", "Unknown")
                temp["city"] = geo_data.get("city", "Unknown")
                temp["network"] = geo_data.get("network", "Unknown")
                data["geolocation"] = temp
    except Exception:
        data["geolocation"] = {"error": f"Unable to get geolocation data"}
    print("Done") if verbose else None

    print("Enrichment complete") if verbose else None
    return data


def _quick_links_url(indicator: str) -> dict:
    quick_links = {
        "VirusTotal": f"https://www.virustotal.com/gui/search/{indicator}",
        "AlienVault OTX": f"https://otx.alienvault.com/indicator/domain/{indicator}",
        "Umbrella": f"https://dashboard.umbrella.com/o/2465322/#/investigate/domain-view/name/{indicator}/view",
        "Shodan": f"https://www.shodan.io/search?query={indicator}",
        "Twitter": f"https://twitter.com/search?q={indicator}",
        "Google": f"https://www.google.com/search?q={indicator}"
    }
    return quick_links


def _quick_links_ip(indicator: str) -> dict:
    quick_links = {
        "VirusTotal": f"https://www.virustotal.com/gui/search/{indicator}",
        "AlienVault OTX": f"https://otx.alienvault.com/indicator/ip/{indicator}",
        "Umbrella": f"https://dashboard.umbrella.com/o/2465322/#/investigate/ip-view/{indicator}",
        "IPalyzer": f"https://ipalyzer.com/{indicator}",
        "Shodan": f"https://www.shodan.io/search?query={indicator}",
        "Twitter": f"https://twitter.com/search?q={indicator}",
        "Google": f"https://www.google.com/search?q={indicator}"
    }
    return quick_links


def get_quick_links(indicator: str) -> dict:
    """Get quick links for an indicator (e.g. VirusTotal, OTX, etc.)

    Args:
        indicator (str): The indicator to get quick links for

    Returns:
        dict: The quick links

    Example:
        .. code-block:: json

            {
                "VirusTotal": "https://www.virustotal.com/gui/search/google.com",
                "AlienVault OTX": "https://otx.alienvault.com/indicator/domain/google.com",
                "Umbrella": "https://dashboard.umbrella.com/o/2465322/#/investigate/domain-view/name/google.com/view",
                "Shodan": "https://www.shodan.io/search?query=google.com",
                "Twitter": "https://twitter.com/search?q=google.com",
                "Google": "https://www.google.com/search?q=google.com"
            }
        ::
    """

    try:
        ip_address(indicator)
        return _quick_links_ip(indicator)
    except:
        return _quick_links_url(indicator)
