# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from collections import OrderedDict


# Amount of bytes (decimal interpretation).
ONE_KB = 1000
ONE_MB = 1000 * ONE_KB
ONE_GB = 1000 * ONE_MB
ONE_TB = 1000 * ONE_GB


# Amount of bytes (binary interpretation).
ONE_KIB = 1024
ONE_MIB = 1024 * ONE_KIB
ONE_GIB = 1024 * ONE_MIB
ONE_TIB = 1024 * ONE_GIB


# Amount of seconds.
ONE_MINUTE = 60
ONE_HOUR = 60 * ONE_MINUTE
ONE_DAY = 24 * ONE_HOUR
ONE_WEEK = 7 * ONE_DAY


# Preferred MIME type for CSV files.
MIMETYPE_CSV = "text/csv"
# Default MIME type for unspecified binary files.
MIMETYPE_DEFAULT = "application/octet-stream"
# Custom MIME type for flow files to define workflows.
MIMETYPE_FLOW = "application/x-flow+json"
# Preferred MIME type for JSON files.
MIMETYPE_JSON = "application/json"
# Custom MIME type for tool files to be used within workflows.
MIMETYPE_TOOL = "application/x-tool+xml"
# Preferred MIME type for XML files.
MIMETYPE_XML = "application/xml"


# URL from which the latest released Kadi version is retrieved.
URL_PYPI = "https://pypi.org/pypi/kadi/json"

# URLs where the documentation is hosted.
URL_RTD_STABLE = "https://kadi4mat.readthedocs.io/en/stable"
URL_RTD_LATEST = "https://kadi4mat.readthedocs.io/en/latest"


# Values for the possible Kadi environments.
ENV_PRODUCTION = "production"
ENV_DEVELOPMENT = "development"
ENV_TESTING = "testing"


# Type values for all built-in storage providers.
STORAGE_TYPE_LOCAL = "local"


# Type values for all built-in authentication providers and corresponding identities.
AUTH_PROVIDER_TYPE_LOCAL = "local"
AUTH_PROVIDER_TYPE_LDAP = "ldap"
AUTH_PROVIDER_TYPE_SHIB = "shib"


# Active state value for all stateful models.
MODEL_STATE_ACTIVE = "active"
# Deleted state value for all stateful models, usually used to represent soft deletion.
MODEL_STATE_DELETED = "deleted"

# Private visibility value for all supporting models.
MODEL_VISIBILITY_PRIVATE = "private"
# Public visibility value for all supporting models, usually used to grant default read
# permission.
MODEL_VISIBILITY_PUBLIC = "public"


# Keys for global config items.
SYS_CONFIG_BROADCAST_MESSAGE = "BROADCAST_MESSAGE"
SYS_CONFIG_NAV_FOOTER_ITEMS = "NAV_FOOTER_ITEMS"
SYS_CONFIG_INDEX_IMAGE = "INDEX_IMAGE"
SYS_CONFIG_INDEX_TEXT = "INDEX_TEXT"

SYS_CONFIG_TERMS_OF_USE = "TERMS_OF_USE"
SYS_CONFIG_PRIVACY_POLICY = "PRIVACY_POLICY"
SYS_CONFIG_ENFORCE_LEGALS = "ENFORCE_LEGALS"
SYS_CONFIG_LEGAL_NOTICE = "LEGAL_NOTICE"

SYS_CONFIG_ROBOTS_NOINDEX = "ROBOTS_NOINDEX"


# Keys for user-specific config items.
USER_CONFIG_HIDE_INTRODUCTION = "HIDE_INTRODUCTION"
USER_CONFIG_HOME_LAYOUT = "HOME_LAYOUT"


# Default values for user-specific config items.
USER_CONFIG_HOME_LAYOUT_DEFAULT = [
    {"resource": "record", "visibility": "all", "creator": "any", "max_items": 6},
    {"resource": "collection", "visibility": "all", "creator": "any", "max_items": 4},
]


# All API versions that are currently available. Defined here, as these are also used in
# places where no application context is available.
API_VERSIONS = ["v1"]


# Currently supported export types with corresponding titles for different resources.
# Defined here, as these are also used in places where no application context is
# available.
EXPORT_TYPES = {
    "record": OrderedDict([("json", "JSON"), ("pdf", "PDF"), ("qr", "QR Code")]),
    "collection": OrderedDict([("json", "JSON"), ("qr", "QR Code")]),
    "template": OrderedDict([("json", "JSON"), ("json-schema", "JSON Schema")]),
}
