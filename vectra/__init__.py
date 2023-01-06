# pylint: disable=line-too-long
"""Package for  the SOC Vectra API Python wrapper."""

from .vectraclient import VectraClient

from .utility import (
    get_dst_ips,
    get_dst_ports,
    get_dst_subnets,
    get_target_domains,
    get_dns_responses,
    add_extra_fields
)
