from django.conf import settings


__all__ = (
    'LAYERS_SORT_ORDER',
    'ICON_ROLE_MAP',
    'ICON_MODEL_MAP',
    'DISPLAY_UNCONNECTED',
    'DISPLAY_LOGICAL_MULTICABLE_LINKS',
    'DISPLAY_PASSIVE_DEVICES',
    'UNDISPLAYED_DEVICE_ROLE_SLUGS',
    'UNDISPLAYED_DEVICE_TAGS',
    'SELECT_LAYERS_LIST_EXCLUDE_DEVICE_TAGS',
    'SELECT_LAYERS_LIST_INCLUDE_DEVICE_TAGS',
    'INITIAL_LAYOUT',
)

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("netbox_topology_plugin", {})

SHOW_CIRCUITS = PLUGIN_SETTINGS.get('show_circuits', True)

LAYERS_SORT_ORDER = PLUGIN_SETTINGS.get("layers_sort_order", ())

ICON_MODEL_MAP = PLUGIN_SETTINGS.get("icon_model_map", {})
ICON_ROLE_MAP = PLUGIN_SETTINGS.get("icon_role_map", {})

DISPLAY_UNCONNECTED = PLUGIN_SETTINGS.get("DISPLAY_UNCONNECTED", True)

# Defines whether logical links between end-devices for multi-cable hops
# are displayed in addition to the physical cabling on the topology view by default or not.
DISPLAY_LOGICAL_MULTICABLE_LINKS = PLUGIN_SETTINGS.get("DISPLAY_LOGICAL_MULTICABLE_LINKS", False)

# Defines whether passive devices
# are displayed on the topology view by default or not.
# Passive devices are patch pannels, power distribution units, etc.
DISPLAY_PASSIVE_DEVICES = PLUGIN_SETTINGS.get("DISPLAY_PASSIVE_DEVICES", False)

# Hide these roles by default
UNDISPLAYED_DEVICE_ROLE_SLUGS = PLUGIN_SETTINGS.get("undisplayed_device_role_slugs", ())

# Defines the initial layer alignment direction on the view
INITIAL_LAYOUT = PLUGIN_SETTINGS.get("INITIAL_LAYOUT", 'auto')

# Hide devices tagged with these tags
UNDISPLAYED_DEVICE_TAGS = PLUGIN_SETTINGS.get("undisplayed_device_tags", ())
# Filter device tags listed in Select Layers menu
SELECT_LAYERS_LIST_INCLUDE_DEVICE_TAGS = PLUGIN_SETTINGS.get("select_layers_list_include_device_tags", ())
SELECT_LAYERS_LIST_EXCLUDE_DEVICE_TAGS = PLUGIN_SETTINGS.get("select_layers_list_exclude_device_tags", ())