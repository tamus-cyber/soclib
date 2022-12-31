"""Module for getting geolocation data for IP addresses and domains."""
import requests

def get_location_data(ip_address: str) -> dict:
    """
    Uses the ipapi.co API to get the country, region code and city of an IP address.

    Parameters:
    - ip_address: str: the IP address for which to get location data

    Returns:
    - dict: a dictionary containing the country, region code and city for the given IP address
    """
    response = requests.get(f"https://ipapi.co/{ip_address}/json/")
    return response.json()
