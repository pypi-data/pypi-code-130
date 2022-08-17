from django.forms import DateField, BooleanField, CharField

from nautobot.extras.forms import AddRemoveTagsForm, CustomFieldBulkEditForm
from nautobot.dcim.models import Manufacturer, Device
from nautobot.extras.forms import CustomFieldModelCSVForm, CustomFieldModelForm, RelationshipModelForm, \
    CustomFieldFilterForm
from nautobot.utilities.forms import CommentField
from nautobot.utilities.forms import StaticSelect2, BOOLEAN_WITH_BLANK_CHOICES
from nautobot.utilities.forms import ExpandableNameField
from .models import SFPType, SFP
from nautobot.utilities.forms import BootstrapMixin, DynamicModelMultipleChoiceField, TagFilterField, SlugField
from nautobot.utilities.forms import widgets
from nautobot.tenancy.models import Tenant
from nautobot.utilities.forms import DynamicModelChoiceField
from nautobot.utilities.forms import CSVModelChoiceField
from django import forms


class SFPTypeFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = SFPType
    q = forms.CharField(required=False, label="Search")

    tag = TagFilterField(model)


class SFPTypeForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    comments = CommentField()

    class Meta:
        model = SFPType
        fields = [
            "name",
            "slug",
            "comments"
        ]


class SFPTypeCSVForm(CustomFieldModelCSVForm):
    class Meta:
        model = SFPType
        fields = [
            "name",
            "slug",
            "comments"
        ]


class SFPFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = SFP
    q = forms.CharField(required=False, label="Search")

    type = DynamicModelMultipleChoiceField(
        queryset=SFPType.objects.all(),
        to_field_name="slug",
        required=False,
        null_option="None",
    )

    manufacturer = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name="slug",
        required=False,
        null_option="None",
    )

    tenant = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="slug",
        required=False,
        null_option="None",
    )

    assigned = forms.NullBooleanField(
        required=False,
        label="Assigned",
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
    )

    assigned_device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        to_field_name="name",
        required=False,
        null_option="None",
        label="Assigned Device"
    )

    tag = TagFilterField(model)


class SFPBulkCreateForm(BootstrapMixin, forms.Form):
    pattern = ExpandableNameField(label="Serial Number")


class SFPForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    type = DynamicModelChoiceField(queryset=SFPType.objects.all(), required=False)
    assigned_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Assigned Device"
    )
    supplier = DynamicModelChoiceField(queryset=Manufacturer.objects.all(), required=False)
    end_of_manufacturer_support = DateField(
        widget=widgets.DatePicker,
        required=False,
        label="End of Manufacturer Support"
    )

    comments = CommentField()

    class Meta:
        model = SFP
        fields = [
            "serial_number",
            "type",
            "dc_tag",
            "asset_tag",
            "tenant",
            "assigned",
            "assigned_device",
            "supplier",
            "end_of_manufacturer_support",
            "comments",
        ]


class SFPBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=SFP.objects.all(), widget=forms.MultipleHiddenInput)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    type = DynamicModelChoiceField(queryset=SFPType.objects.all(), required=False)
    assigned = BooleanField(required=False)
    assigned_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Assigned Device"
    )
    supplier = DynamicModelChoiceField(queryset=Manufacturer.objects.all(), required=False)
    end_of_manufacturer_support = DateField(
        widget=widgets.DatePicker,
        required=False,
        label="End of Manufacturer Support"
    )

    comments = CommentField()

    class Meta:
        nullable_fields = [
            "assigned",
            "end_of_manufacturer_support",
            "comments",
        ]


class SFPCSVForm(CustomFieldModelCSVForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Assigned tenant",
    )

    type = CSVModelChoiceField(
        queryset=SFPType.objects.all(),
        to_field_name="slug",
        required=True,
    )

    assigned_device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name="name",
        required=False,
    )

    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name="name",
        required=True,
    )

    class Meta:
        model = SFP
        fields = [
            "serial_number",
            "type",
            "dc_tag",
            "asset_tag",
            "tenant",
            "assigned",
            "assigned_device",
            "supplier",
            "end_of_manufacturer_support",
            "comments",
        ]
