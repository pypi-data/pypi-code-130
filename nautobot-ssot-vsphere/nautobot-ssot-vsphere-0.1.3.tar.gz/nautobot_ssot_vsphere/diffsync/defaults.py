"""Default settings to use across different files."""
from django.conf import settings

CONFIG = settings.PLUGINS_CONFIG.get("nautobot_ssot_vsphere", {})
DEFAULT_VSPHERE_TYPE = CONFIG.get("VSPHERE_TYPE", "VMWare vSphere")
ENFORCE_CLUSTER_GROUP_TOP_LEVEL = CONFIG.get("ENFORCE_CLUSTER_GROUP_TOP_LEVEL", True)
VSPHERE_USERNAME = CONFIG["VSPHERE_USERNAME"]
VSPHERE_PASSWORD = CONFIG["VSPHERE_PASSWORD"]
VSPHERE_VERIFY_SSL = CONFIG.get("VSPHERE_VERIFY_SSL", False)
VSPHERE_URI = CONFIG["VSPHERE_URI"]
DEFAULT_VM_STATUS_MAP = CONFIG.get("VSPHERE_VM_STATUS_MAP", {"POWERED_OFF": "Offline", "POWERED_ON": "Active"})
DEFAULT_IP_STATUS_MAP = CONFIG.get("VSPHERE_IP_STATUS_MAP", {"PREFERRED": "Active", "UNKNOWN": "Reserved"})
VSPHERE_VM_INTERFACE_MAP = CONFIG.get("VSPHERE_VM_INTERFACE_MAP", {"NOT_CONNECTED": False, "CONNECTED": True})
PRIMARY_IP_SORT_BY = CONFIG.get("PRIMARY_IP_SORT_BY", "Lowest")
DEFAULT_USE_CLUSTERS = CONFIG.get("DEFAULT_USE_CLUSTERS", True)
DEFAULT_CLUSTER_NAME = CONFIG.get("DEFAULT_CLUSTER_NAME", "vSphere Default Cluster")
DEFAULT_IGNORE_LINK_LOCAL = CONFIG.get("DEFAULT_IGNORE_LINK_LOCAL", True)
