"""Library of functions for reading and searching stakeholder data"""

import os
import ipaddress
import pylightxl as xl
from soclib.stakeholder.soc_db_utils import ip_lookup_db
import re

def init_stakeholder_ip_data(file_path):
    '''
    Reads the stakeholder data from .xlsx files in the networks folder
    and returns a dictionary with the data stored as a pandas DataFrame object.
    '''
    # Get list of files in networks folder
    stakeholder_list = []
    for file in os.listdir(file_path):
        if file.endswith(".xlsx"):
            stakeholder_list.append(file.split(".")[0])

    # Load data from ip range .xlsx files into pandas DataFrame objects
    stakeholder_files = {}
    for stakeholder in stakeholder_list:
        try:
            stakeholder_files[stakeholder] = xl.readxl(
                file_path+ "/" + stakeholder + ".xlsx")
        except Exception as e:
            response = {"status": "error", "error": type(
                e).__name__, "stakeholder": stakeholder}
            return response

    response = {"status": "success", "data": {
        "stakeholder_ip_files": stakeholder_files, "stakeholder_list": stakeholder_list}}
    return response


def search_stakeholder(stakeholder, stakeholder_file, ip_address):
    try:
        ip_address = ipaddress.ip_address(ip_address)
    except:
        return {"status": "error", "error": "Invalid IP address"}
    found_networks = []
    sheet = stakeholder_file.ws_names[0]
    sheet_rows = stakeholder_file.ws(ws=sheet).rows
    for row in sheet_rows:
        network = row[0]
        comment = row[1]
        try:
            # Check if the row is a header
            if network == "Network":
                continue

            if ip_address in ipaddress.ip_network(network, False):
                network = {"network": network, "comment": comment,
                        "stakeholder": stakeholder, "location": ""}
                if stakeholder == "TAMU":
                    try:
                        network["location"] = str(row[2])
                    except:
                        network["location"] = ""
                network["query"] = ip_address
                found_networks.append(network)
        except Exception as e:
            pass
    if len(found_networks) == 0:
        return {"status": "error", "error": "No networks found"}
    return {"status": "success", "data": found_networks}


def validate_ips(ip_address):
    '''
    Validates a list of IPv4 addresses

    Args:
        ip_address (list): List of IPv4 addresses

    Returns:
        dict: Dictionary with the following keys:
            status (str): "success" or "error"
            error (str): Error message if status is "error"
            data (dict): Dictionary with the following keys:
                valid_ips (list): List of valid IPv4 addresses
                invalid_ips (list): List of invalid IPv4 addresses
    '''
    valid_ips = []
    invalid_ips = []
    for ip in ip_address:
        try:
            ipaddress.ip_address(ip)
            valid_ips.append(ip)
        except ValueError:
            invalid_ips.append(ip)
    return {"status": "success", "data": {"valid_ips": valid_ips, "invalid_ips": invalid_ips}}


def ip_lookup_xlsx(ip_address, stakeholder_ip_files, stakeholder_list):
    '''
    This is the old version that uses the .xlsx files to search for networks.

    When looking up a large list of IP's, the function will check each one against subnets that have already been found
    in order to avoid duplicate searches. This is useful when looking up a large number of IP's that
    likely belong to the same subnet. I.E., there is no reason to look up every IP in 10.1.1.0/24 in scanning detection
    when we aready have a result for 10.1.1.0/24

    Args:
        ipaddress (list or str): List or string of valid IP addresses to look up
        stakeholder_ip_files (dict): Dictionary with the following keys:
            'stakeholder': stakeholder_file (DataFrame): Pandas DataFrame object with the IP ranges for the stakeholder
        stakeholder_list (list): List of stakeholder names

    Returns:
        dict: Dictionary with the following keys:
            status (str): "success" or "error"
            error (str): Error message if status is "error"
            data (dict): Dictionary with the following keys:
                found_networks (list): List of networks that were found
                invalid_ips (list): List of invalid IP addresses
    '''
    found_networks = []  # Will store network data to display to user, speperate for each stakeholder
    subnet_cache = {stakeholder: [] for stakeholder in stakeholder_list}  # Will store subnets that have already been searched
    ip_address = [ip_address] if type(ip_address) is not list else ip_address  # Convert to list if not already

    # Validate IP addresses
    results = validate_ips(ip_address)
    if results["status"] == "error":
        return results
    ip_address = results["data"]["valid_ips"]

    # make a progress bar visible only if there is more than one IP address to search
    for ip in ip_address:
        for stakeholder in stakeholder_list:
            # Check if IP has already been searched
            if any(ipaddress.ip_address(ip) in subnet for subnet in subnet_cache[stakeholder]):
                continue

            response = search_stakeholder(stakeholder, stakeholder_ip_files[stakeholder], ip)
            if response["status"] == "success":
                # Cache subnet(s) that have been found
                for network in response["data"]:
                    subnet_cache[stakeholder].append(ipaddress.ip_network(network['network']))
                found_networks.extend(response["data"])

    return {"status": "success", "data": {"found_networks": found_networks, "invalid_ips": results["data"]["invalid_ips"]}}


def extract_ips_from_text(text):
    possible_ips = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', text)
    valid_ips = []
    for ip in possible_ips:
        try:
            if ipaddress.ip_address(ip):
                valid_ips.append(ip)
        except ValueError:
            pass
    return valid_ips

def lookup_ip(query: str, connection=None, stakeholder_ip_files=None, stakeholder_list=None):
    if connection is None:
        if stakeholder_ip_files is None or stakeholder_list is None:
            raise ValueError("If connection is None, stakeholder_ip_files and stakeholder_list must be provided")

    # If user entered multiple IP addresses, split them into a list
    ip_address = extract_ips_from_text(query)
    if connection is None:
        results = ip_lookup_xlsx(ip_address, stakeholder_ip_files, stakeholder_list)
    else:
        results = ip_lookup_db.ip_lookup_db(ip_address, connection)
    return results