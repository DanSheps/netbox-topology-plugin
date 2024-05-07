from django.conf import settings

from netbox.plugins import PluginConfig

from importlib.metadata import metadata


class NetBoxTopologyConfig(PluginConfig):
    name = metadata("netbox_topology_plugin").get('Name').replace('-', '_')
    verbose_name = "Netbox Topology Plugin"
    description = metadata("netbox_topology_plugin").get('Summary') #metadata("netbox_topology_plugin").get('Description')
    version = metadata("netbox_topology_plugin").get('Version')
    author = metadata("netbox_topology_plugin").get("Author-email")
    author_email = metadata("netbox_topology_plugin").get("Author-email")
    base_url = 'topology'
    required_settings = []
    default_settings = {
        'layers_sort_order': (
            'undefined',
            'circuit',
            'outside',
            'border',
            'edge',
            'edge-switch',
            'edge-router',
            'core',
            'core-router',
            'core-switch',
            'distribution',
            'distribution-router',
            'distribution-switch',
            'leaf',
            'spine',
            'access',
            'access-switch',
        ),
        'icon_model_map': {
            'CSR1000V': 'router',
            'Nexus': 'switch',
            'IOSXRv': 'router',
            'IOSv': 'switch',
            '2901': 'router',
            '2911': 'router',
            '2921': 'router',
            '2951': 'router',
            '4321': 'router',
            '4331': 'router',
            '4351': 'router',
            '4421': 'router',
            '4431': 'router',
            '4451': 'router',
            '2960': 'switch',
            '3750': 'switch',
            '3850': 'switch',
            'ASA': 'firewall',
        },
        'icon_role_map': {
            'border': 'router',
            'edge-switch': 'switch',
            'edge-router': 'router',
            'core-router': 'router',
            'core-switch': 'switch',
            'distribution': 'switch',
            'distribution-router': 'router',
            'distribution-switch': 'switch',
            'leaf': 'switch',
            'spine': 'switch',
            'access': 'switch',
            'access-switch': 'switch',
        },
        'DISPLAY_UNCONNECTED': True,
        'DISPLAY_LOGICAL_MULTICABLE_LINKS': False,
        'DISPLAY_PASSIVE_DEVICES': False,
        'undisplayed_device_role_slugs': (),
        'undisplayed_device_tags': (),
        'select_layers_list_include_device_tags': (),
        'select_layers_list_exclude_device_tags': (),
        'INITIAL_LAYOUT': 'auto',
    }
    caching_config = {
        '*': None
    }

    def ready(self):
        super().ready()
        PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("netbox_topology_plugin", {})
        INITIAL_LAYOUT = PLUGIN_SETTINGS.get("INITIAL_LAYOUT", 'auto')
        if INITIAL_LAYOUT not in ('vertical', 'horizontal', 'auto'):
            INITIAL_LAYOUT = 'auto'


config = NetBoxTopologyConfig
