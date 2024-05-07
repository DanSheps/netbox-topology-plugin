from django import forms
from ipam.models import VLAN
from .models import SavedTopology
from dcim.models import Device, Site, Region

from dcim.models import Location
from django.utils.translation import gettext as _
from utilities.forms.fields import (
    DynamicModelMultipleChoiceField,
    DynamicModelChoiceField
)


class TopologyFilterForm(forms.Form):

    model = Device

    device_id = DynamicModelMultipleChoiceField(
        label=_('Devices'),
        queryset=Device.objects.all(),
        to_field_name='id',
        required=False,
        null_option='None',
    )
    location_id = DynamicModelMultipleChoiceField(
        label=_('Location'),
        queryset=Location.objects.all(),
        required=False,
        to_field_name='id',
        null_option='None',
    )
    site_id = DynamicModelMultipleChoiceField(
        label=_('Sites'),
        queryset=Site.objects.all(),
        required=False,
        to_field_name='id',
        null_option='None',
    )
    vlan_id = DynamicModelChoiceField(
        label=_('Vlan'),
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='id',
        null_option='None',
    )
    region_id = DynamicModelMultipleChoiceField(
        label=_('Regions'),
        queryset=Region.objects.all(),
        required=False,
        to_field_name='id',
        null_option='None',
    )


class LoadSavedTopologyFilterForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(LoadSavedTopologyFilterForm, self).__init__(*args, **kwargs)
        self.fields['saved_topology_id'].queryset = SavedTopology.objects.filter(created_by=user)

    model = SavedTopology

    saved_topology_id = forms.ModelChoiceField(
        queryset=None,
        to_field_name='id',
        required=True
    )
