"""Module for getting geolocation data for IP addresses and domains."""
import requests

def get_location_data(ip_address: str) -> dict:
    """
    Uses the ipapi.co API to get the country, region code and city of an IP address.

    Args:
        ip_address (str): the IP address for which to get location data

    Returns:
        dict: a dictionary containing the country, region code and city for the given IP address

    Example:
        .. code-block:: json

            {
                "ip": "8.8.8.8",
                "network": "8.8.8.0/24",
                "version": "IPv4",
                "city": "Mountain View",
                "region": "California",
                "region_code": "CA",
                "country": "US",
                "country_name": "United States",
                "country_code": "US",
                "country_code_iso3": "USA",
                "country_capital": "Washington",
                "country_tld": ".us",
                "continent_code": "NA",
                "in_eu": false,
                "postal": "94043",
                "latitude": 37.42301,
                "longitude": -122.083352,
                "timezone": "America/Los_Angeles",
                "utc_offset": "-0700",
                "country_calling_code": "+1",
                "currency": "USD",
                "currency_name": "Dollar",
                "languages": "en-US,es-US,haw,fr",
                "country_area": 9629091.0,
                "country_population": 327167434,
                "asn": "AS15169",
                "org": "GOOGLE"
            }
        ::
    """
    response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=5)
    return response.json()
