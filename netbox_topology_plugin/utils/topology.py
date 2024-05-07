from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from circuits.models import CircuitTermination
from dcim.models import DeviceRole, Interface, Cable, PowerFeed
from ipam.models import VLAN
from netbox_topology_plugin.models import SavedTopology
from netbox_topology_plugin.settings import LAYERS_SORT_ORDER, UNDISPLAYED_DEVICE_ROLE_SLUGS, SHOW_CIRCUITS
from netbox_topology_plugin.utils.filtering import tag_is_hidden, filter_tags
from netbox_topology_plugin.utils.icons import get_icon_type
from netbox_topology_plugin.utils.interfaces import if_shortname


__all__ = (
    'get_node_layer_sort_preference',
    'get_vlan_topology',
    'get_topology',
    'get_saved_topology',
)


def get_node_layer_sort_preference(device_role):
    """Layer priority selection function
    Layer sort preference is designed as numeric value.
    This function identifies it by LAYERS_SORT_ORDER
    object position by default. With numeric values,
    the logic may be improved without changes on NeXt app side.
    0(null) results undefined layer position in NeXt UI.
    Valid indexes start with 1.
    """
    for i, role in enumerate(LAYERS_SORT_ORDER, start=1):
        if device_role == role:
            return i
    return 1


def get_vlan_topology(nb_devices_qs, vlans):

    topology_dict = {'nodes': [], 'links': []}
    device_roles = set()
    all_device_tags = set()
    multi_cable_connections = []
    vlan = VLAN.objects.get(id=vlans)
    interfaces = vlan.get_interfaces()
    filtred_devices = [d.id for d in nb_devices_qs]
    filtred_interfaces = []
    for interface in interfaces:
        if interface.is_connectable:
            direct_device_id = interface.device.id
            interface_trace = interface.trace()
            if len(interface_trace) != 0:
                termination_b_iface = interface_trace[-1][-1]
                connected_device_id = termination_b_iface.device.id
                if (direct_device_id in filtred_devices) or (direct_device_id in filtred_devices):
                    filtred_interfaces.append(interface)

    devices = []
    for interface in filtred_interfaces:
        if interface.is_connectable:
            if interface.device not in devices:
                devices.append(interface.device)
            interface_trace = interface.trace()
            if len(interface_trace) != 0:
                termination_b_iface = interface_trace[-1][-1]
                if termination_b_iface.device not in devices:
                    devices.append(termination_b_iface.device)

    device_ids = [d.id for d in devices]
    for device in devices:
        device_is_passive = False
        device_url = device.get_absolute_url()
        primary_ip = ''
        if device.primary_ip:
            primary_ip = str(device.primary_ip.address)
        tags = [str(tag) for tag in device.tags.names()]
        for tag in tags:
            all_device_tags.add((tag, not tag_is_hidden(tag)))
        topology_dict['nodes'].append({
            'id': device.id,
            'name': device.name,
            'dcimDeviceLink': device_url,
            'primaryIP': primary_ip,
            'serial_number': device.serial,
            'model': device.device_type.model,
            'deviceRole': device.role.slug,
            'layerSortPreference': get_node_layer_sort_preference(
                device.role.slug
            ),
            'icon': get_icon_type(
                device
            ),
            'isPassive': device_is_passive,
            'tags': tags,
        })
        is_visible = not (device.role.slug in UNDISPLAYED_DEVICE_ROLE_SLUGS)
        device_roles.add((device.role.slug, device.role.name, is_visible))

    mapped_links = []
    for interface in filtred_interfaces:
        if interface.is_connectable:
            interface_trace = interface.trace()
            if len(interface_trace) != 0:
                source_cable = interface_trace[0]
                dest_cable = interface_trace[-1]
                mapping_link = [source_cable[0].device.id, dest_cable[-1].device.id]
                if (mapping_link not in mapped_links) and (mapping_link.reverse() not in mapped_links):
                    mapped_links.append(mapping_link)

                    topology_dict['links'].append({
                        'id': source_cable[1].id,
                        'dcimCableURL': source_cable[1].get_absolute_url(),
                        'label': f"Cable {source_cable[1].id}",
                        'source': source_cable[0].device.id,
                        'target': dest_cable[-1].device.id,
                        'sourceDeviceName': source_cable[0].device.name,
                        'targetDeviceName': dest_cable[-1].device.name,
                        "srcIfName": if_shortname(source_cable[0].name),
                        "tgtIfName": if_shortname(dest_cable[-1].name),
                    })

    return topology_dict, device_roles, multi_cable_connections, list(all_device_tags)


def get_topology(nb_devices_qs):
    ct_endpoints = ContentType.objects.filter(
        Q(app_label='circuits', model__in=('circuittermination',)) |
        Q(app_label='dcim', model__in=('interface',))
    )
    ct_interface = ContentType.objects.get(app_label='dcim', model='interface')
    ct_circuittermination = ContentType.objects.get(app_label='circuits', model='circuittermination')
    topology_dict = {'nodes': [], 'links': []}
    device_roles = set()
    all_device_tags = set()
    multi_cable_connections = []
    if not nb_devices_qs:
        return topology_dict, device_roles, multi_cable_connections, list(all_device_tags)
    links = []
    device_ids = [d.id for d in nb_devices_qs]
    for device in nb_devices_qs:
        device_url = device.get_absolute_url()
        primary_ip = ''
        if device.primary_ip:
            primary_ip = str(device.primary_ip.address)
        tags = [str(tag) for tag in device.tags.names()] or []
        tags = filter_tags(tags)
        for tag in tags:
            all_device_tags.add((tag, not tag_is_hidden(tag)))
        # Device is considered passive if it has no linked Interfaces.
        # Passive cabling devices use Rear and Front Ports.
        device_links = Cable.objects.filter(
            terminations___device_id=1,
            terminations__termination_type__in=(ct_interface, )
        )
        interfaces_found = False
        if device_links.count() > 0:
            interfaces_found = True
        device_is_passive = not interfaces_found

        topology_dict['nodes'].append({
            'id': device.id,
            'name': device.name,
            'dcimDeviceLink': device_url,
            'primaryIP': primary_ip,
            'serial_number': device.serial,
            'model': device.device_type.model,
            'deviceRole': device.role.slug,
            'layerSortPreference': get_node_layer_sort_preference(
                device.role.slug
            ),
            'icon': get_icon_type(
                device
            ),
            'isPassive': device_is_passive,
            'tags': tags,
        })
        is_visible = not (device.role.slug in UNDISPLAYED_DEVICE_ROLE_SLUGS)
        device_roles.add((device.role.slug, device.role.name, is_visible))
        if not device_links:
            continue
        for link in device_links:
            # Exclude CircuitTermination-connected links
            if link.terminations.filter(termination_type=ct_circuittermination).count() > 0 and not SHOW_CIRCUITS:
                continue
            # Include CircuitTermination-connected links
            elif link.terminations.filter(termination_type=ct_circuittermination).count()>0 and SHOW_CIRCUITS:
                links.append(link)
                termination = link.terminations.filter(termination_type=ct_circuittermination).first().termination
                topology_dict['nodes'].append({
                    'id': f'cid-{termination.id}',
                    'name': termination.circuit.cid,
                    'dcimDeviceLink': termination.circuit.get_absolute_url(),
                    'primaryIP': None,
                    'serial_number': None,
                    'model': None,
                    'deviceRole': None,
                    'layerSortPreference': 1,
                    'icon': 'circuit',
                    'isPassive': False,
                    'tags': [],
                })
            # Include links to discovered devices only
            elif link.b_terminations[0].device_id in device_ids:
                links.append(link)
    device_roles = list(device_roles)
    device_roles.sort(key=lambda i: get_node_layer_sort_preference(i[0]))
    all_device_tags = list(all_device_tags)
    all_device_tags.sort()
    if not links:
        return topology_dict, device_roles, multi_cable_connections, list(all_device_tags)
    link_ids = set()

    for link in links:
        link_ids.add(link.id)
        link_url = link.get_absolute_url()
        termination_a = link.a_terminations[0]
        termination_b = link.b_terminations[0]
        if isinstance(termination_a, Interface):
            source = {
                'id': termination_a.device.id,
                'deviceName': termination_a.device.name,
                'interfaceName': termination_a.name
            }
        elif isinstance(termination_a, CircuitTermination):
            source = {
                'id': f'cid-{termination_a.id}',
                'deviceName': termination_a.circuit.cid,
                'interfaceName': termination_a.term_side
            }
        if isinstance(termination_b, Interface):
            destination = {
                'id': termination_b.device.id,
                'deviceName': termination_b.device.name,
                'interfaceName': termination_b.name
            }
        elif isinstance(termination_b, CircuitTermination):
            destination = {
                'id': f'cid-{termination_b.id}',
                'deviceName': termination_b.circuit.cid,
                'interfaceName': termination_b.term_side
            }

        topology_dict['links'].append({
            'id': link.id,
            'label': f"Cable {link.id}",
            'dcimCableURL': link_url,
            'source': source['id'],
            'target': destination['id'],
            'sourceDeviceName': source['deviceName'],
            'targetDeviceName': destination['deviceName'],
            "srcIfName": if_shortname(source['interfaceName']),
            "tgtIfName": if_shortname(destination['interfaceName'])
        })
        if not (isinstance(termination_a, Interface) or isinstance(termination_b, Interface)):
            # Skip trace if none of cable terminations is an Interface
            continue
        else:
            interface_side = None
            if isinstance(termination_a, Interface):
                interface_side = termination_a
            elif isinstance(termination_b, Interface):
                interface_side = termination_b
            trace_result = interface_side.trace()
            if not trace_result:
                continue
            cable_path = trace_result

            # identify segmented cable paths between end-devices
            if len(cable_path) < 2:
                continue

            if isinstance(cable_path[0][0], Interface) and isinstance(cable_path[-1][2], Interface):
                if set([c[1] for c in cable_path]) in [set([c[1] for c in x]) for x in multi_cable_connections]:
                    continue
                multi_cable_connections.append(cable_path)
    for cable_path in multi_cable_connections:
        link_id = max(link_ids) + 1  # dummy ID for a logical link
        link_ids.add(link_id)
        topology_dict['links'].append({
            'id': link_id,
            'source': cable_path[0][0].device.id,
            'target': cable_path[-1][2].device.id,
            "srcIfName": if_shortname(cable_path[0][0].name),
            "tgtIfName": if_shortname(cable_path[-1][2].name),
            "isLogicalMultiCable": True,
        })
    return topology_dict, device_roles, multi_cable_connections, all_device_tags


def get_saved_topology(id):
    topology_dict = {}
    device_roles = []
    device_tags = []
    device_roles_detailed = []
    device_tags_detailed = []
    layout_context = {}
    topology_data = SavedTopology.objects.get(id=id)
    if not topology_data:
        return topology_dict, device_roles, device_tags, layout_context
    topology_dict = dict(topology_data.topology)
    if 'nodes' not in topology_dict:
        return topology_dict, device_roles, device_tags, layout_context
    device_roles = list(set([str(d.get('deviceRole')) for d in topology_dict['nodes'] if d.get('deviceRole')]))
    for device_role in device_roles:
        is_visible = not (device_role in UNDISPLAYED_DEVICE_ROLE_SLUGS)
        device_role_obj = DeviceRole.objects.get(slug=device_role)
        if not device_role_obj:
            device_roles_detailed.append((device_role, device_role, is_visible))
            continue
        device_roles_detailed.append((device_role_obj.slug, device_role_obj.name, is_visible))
    device_roles_detailed.sort(key=lambda i: get_node_layer_sort_preference(i[0]))
    device_tags = set()
    for device in topology_dict['nodes']:
        if 'tags' not in device:
            continue
        for tag in device['tags']:
            device_tags.add(str(tag))
    device_tags = list(device_tags)
    device_tags_detailed = list([(tag, not tag_is_hidden(tag)) for tag in device_tags])
    layout_context = dict(topology_data.layout_context)
    return topology_dict, device_roles_detailed, device_tags_detailed, layout_context