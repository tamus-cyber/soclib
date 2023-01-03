# pylint: disable-all
#!/usr/bin/env python3
from ipaddress import ip_address
from rich.pretty import pprint
from soclib.reputation.otx import AlienVaultOTXClient
from soclib.reputation.umbrella import UmbrellaClient
from soclib.geolocation import get_location_data
from soclib.misc import get_website_description

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
            return {"error": "Private IP address"}
    except ValueError:
        data["indicator_type"] = "domain"
        # Resolve the domain so we can get the ASN later
        try:
            print(f"Resolving {indicator}...", end=" ") if verbose else None
            data["ip_address"] = umbrella_session.resolve_domain(indicator)
            print(f"Done ({data['ip_address']})") if verbose else None
        except Exception as err:
            data["ip_address"] = None
            print(f"Failed ({err})") if verbose else None

    
    # Enrich the indicator
    # OTX
    print("Getting OTX data...", end=" ") if verbose else None
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

    print("Getting Umbrella data...", end=" ") if verbose else None
    # Umbrella
    data["umbrella"]['categories'] = umbrella_session.get_domain_category(indicator)
    if data["ip_address"] is not None:
        data["umbrella"]['asn'] = umbrella_session.get_asn(data["ip_address"])
    print("Done") if verbose else None

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

    # Get website description (meta description)
    print("Getting website description...", end=" ") if verbose else None
    if data["indicator_type"] == "domain":
        try:
            data["website_description"] = get_website_description(indicator)
        except Exception:
            data["website_description"] = {"error": f"Unable to get website description"}
    print("Done") if verbose else None
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
    """

    try:
        ip_address(indicator)
        return _quick_links_ip(indicator)
    except:
        return _quick_links_url(indicator)
