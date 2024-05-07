from netbox_topology_plugin.constants.icons import SUPPORTED_ICONS
from netbox_topology_plugin.settings import ICON_MODEL_MAP, ICON_ROLE_MAP


__all__ = (
    'get_icon_type',
)

#
# Get Types
#
def get_icon_type(device):
    """
    Node icon getter function.
    Selection order:
    1. Based on 'icon_{icon_type}' tag in Netbox device
    2. Based on Netbox device type and ICON_MODEL_MAP
    3. Based on Netbox device role and ICON_ROLE_MAP
    4. Default 'undefined'
    """
    if not device:
        return 'unknown'
    for tag in device.tags.names():
        if 'icon_' in tag:
            if tag.replace('icon_', '') in SUPPORTED_ICONS:
                return tag.replace('icon_', '')
    for model_base, icon_type in ICON_MODEL_MAP.items():
        if model_base in str(device.device_type.model):
            return icon_type
    for role_slug, icon_type in ICON_ROLE_MAP.items():
        if str(device.role.slug) == role_slug:
            return icon_type
    return 'unknown'
