from django.shortcuts import render
from django.views.generic import View
from dcim.models import Device
from .models import SavedTopology
from . import forms, filters
from django.contrib.auth.mixins import PermissionRequiredMixin
import json

from .settings import UNDISPLAYED_DEVICE_ROLE_SLUGS, DISPLAY_LOGICAL_MULTICABLE_LINKS, DISPLAY_UNCONNECTED, \
    INITIAL_LAYOUT, DISPLAY_PASSIVE_DEVICES, UNDISPLAYED_DEVICE_TAGS
from .utils.topology import get_saved_topology, get_topology, get_vlan_topology


class TopologyView(PermissionRequiredMixin, View):
    """Generic Topology View"""
    permission_required = ('dcim.view_site', 'dcim.view_device', 'dcim.view_cable')
    queryset = Device.objects.all()
    filterset = filters.TopologyFilterSet
    template_name = 'netbox_topology_plugin/topology.html'

    def get(self, request):

        if not request.GET:
            self.queryset = Device.objects.none()
        elif 'saved_topology_id' in request.GET:
            self.queryset = Device.objects.none()

        saved_topology_id = request.GET.get('saved_topology_id')
        layout_context = {}

        if saved_topology_id is not None:
            topology_dict, device_roles, device_tags, layout_context = get_saved_topology(saved_topology_id)
        else:
            vlans = []
            if 'vlan_id' in request.GET:
                clean_request = request.GET.copy()
                clean_request.pop('vlan_id')
                vlans = request.GET.get('vlan_id')
            else:
                clean_request = request.GET.copy()

            self.queryset = self.filterset(clean_request, self.queryset).qs
            if len(vlans) == 0:
                topology_dict, device_roles, multi_cable_connections, device_tags = get_topology(self.queryset)
            else:
                topology_dict, device_roles, multi_cable_connections, device_tags = get_vlan_topology(self.queryset, vlans)

        return render(request, self.template_name, {
            'source_data': json.dumps(topology_dict),
            'display_unconnected': layout_context.get('displayUnconnected') or DISPLAY_UNCONNECTED,
            'device_roles': device_roles,
            'device_tags': device_tags,
            'undisplayed_roles': list(UNDISPLAYED_DEVICE_ROLE_SLUGS),
            'undisplayed_device_tags': list(UNDISPLAYED_DEVICE_TAGS),
            'display_logical_multicable_links': DISPLAY_LOGICAL_MULTICABLE_LINKS,
            'display_passive_devices': layout_context.get('displayPassiveDevices') or DISPLAY_PASSIVE_DEVICES,
            'initial_layout': INITIAL_LAYOUT,
            'filter_form': forms.TopologyFilterForm(
                layout_context.get('requestGET') or request.GET,
                label_suffix=''
            ),
            'load_saved_filter_form': forms.LoadSavedTopologyFilterForm(
                request.GET,
                label_suffix='',
                user=request.user
            ),
            'load_saved': SavedTopology.objects.all(), 
            'requestGET': dict(request.GET),
        })


class SiteTopologyView(TopologyView):
    template_name = 'netbox_topology_plugin/site_topology.html'
