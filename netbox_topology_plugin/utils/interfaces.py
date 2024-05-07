from netbox_topology_plugin.constants.interfaces import INTERFACE_FULL_NAME_MAP


__all__ = (
    'if_shortname',
)


def if_shortname(ifname):
    for k, v in INTERFACE_FULL_NAME_MAP.items():
        if ifname.startswith(v):
            return ifname.replace(v, k)
    return ifname