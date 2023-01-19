# pylint: disable=line-too-long
"""Collection of functions to help with handling Vectra detections."""

from loguru import logger
logger.disable(__name__)


def get_hostnames(detection: dict) -> set:
    """Get hostname from a Vectra detection.

    Args:
        detection (dict): Vectra detection JSON dictionary.

    Returns:
        str: Hostname.
    """
    hosts = set()
    hostname = detection.get("src_host", {}).get("name", None)
    if hostname:
        hosts.add(hostname)
    logger.trace(f'Hosts: {hosts}')
    return hosts


def get_src_ip(detection: dict) -> str:
    """Get source IP from a Vectra detection.

    Args:
        detection (dict): Vectra detection JSON dictionary.

    Returns:
        str: Source IP.
    """
    src_ip = detection.get("src_ip", None)
    logger.trace(f'Source IP: {src_ip}')
    return src_ip


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

    logger.trace(f'Destination IPs: {dst_ips}')
    return dst_ips


def get_related_ips(detection: dict) -> set:
    """Get related IPs from a Vectra detection.

    Args:
        detection (dict): Vectra detection JSON dictionary.

    Returns:
        set: Set of related IPs.
    """
    related_ips = set()

    # Combine src_ip and dst_ips into a single set.
    related_ips.add(get_src_ip(detection))
    for dst_ip in get_dst_ips(detection):
        related_ips.add(dst_ip)

    logger.trace(f'Related IPs: {related_ips}')
    return related_ips


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

    logger.trace(f'Destination subnets: {dst_subnets}')
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

    logger.trace(f'Destination ports: {dst_ports}')
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

    logger.debug(f'Target domains: {target_domains}')
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

    logger.trace(f'DNS responses: {dns_responses}')
    return dns_responses


def get_accounts(detection: dict) -> set:
    """Get accounts from a Vectra detection.

    Args:
        detection (dict): Vectra detection JSON dictionary.

    Returns:
        set: Set of accounts.
    """
    accounts = set()

    # Check summary if present
    for account in detection.get('summary', {}).get('src_accounts', []):
        if account.get('name', None):
            accounts.add(account['name'])

    # Check grouped_details if present
    for group in detection.get("grouped_details", []):
        if group.get('src_account', {}).get('name', None):
            accounts.add(group['src_account']['name'])

    logger.trace(f'Accounts: {accounts}')
    return accounts


def get_risk_score(detection: dict) -> int:
    """Get risk score from a Vectra detection.

    Args:
        detection (dict): Vectra detection JSON dictionary.

    Returns:
        int: Risk score.
    """
    threat = detection.get('threat', None)
    certainty = detection.get('certainty', None)

    # If either threat or certainty is None, return None
    if threat is None or certainty is None:
        logger.trace('Risk score: None')
        return None

    # Risk score is threat * certainty normalized (Braxton/Mike's request)
    risk_score = int((threat * certainty) / 100)

    logger.trace(f'Risk score: {risk_score}')
    return risk_score


def get_host_risk_score(detection: dict) -> int:
    """Get risk score from a Vectra detection's host.

    Args:
        detection (dict): Vectra detection JSON dictionary.

    Returns:
        int: Host risk score.
    """
    threat = detection.get("src_host", {}).get('threat', None)
    certainty = detection.get("src_host", {}).get('certainty', None)

    # If either threat or certainty is None, return None
    if threat is None or certainty is None:
        logger.trace('Risk score: None')
        return None

    # Risk score is threat * certainty normalized (Braxton/Mike's request)
    risk_score = int((threat * certainty) / 100)

    logger.trace(f'Risk score: {risk_score}')
    return risk_score


def get_groups(detection: dict) -> list:
    """Get groups the source host is in

    Args:
        detection (dict): Vectra detection JSON dictionary.

    Returns:
        set: Vectra source host groups
    """
    groups = set()
    # Get from groups and src_host.groups
    combined_groups = detection.get("src_host", {}).get("groups", []) + detection.get("groups", [])
    for group in combined_groups:
        group_name = group.get("name", None)
        group_description = group.get("description", None)
        # Concatenate name and description if both are present
        if group_name and group_description:
            groups.add(f"{group_name} - {group_description}")
    return list(groups)


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
            logger.warning(f'Extra field "{key}" already exists in detection. Not overwriting.')
    return detection
