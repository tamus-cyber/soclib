# pylint: disable=line-too-long
"""Package for  the SOC Vectra API Python wrapper."""

__all__ = [
    "VectraClient",
    "get_hostnames",
    "get_src_ip",
    "get_dst_ips",
    "get_related_ips",
    "get_dst_subnets",
    "get_dst_ports",
    "get_target_domains",
    "get_dns_responses",
    "get_groups",
    "add_extra_fields"
]

from .vectraclient import VectraClient

from .utility import (
    get_hostnames,
    get_src_ip,
    get_dst_ips,
    get_related_ips,
    get_dst_subnets,
    get_dst_ports,
    get_target_domains,
    get_dns_responses,
    get_groups,
    add_extra_fields
)
