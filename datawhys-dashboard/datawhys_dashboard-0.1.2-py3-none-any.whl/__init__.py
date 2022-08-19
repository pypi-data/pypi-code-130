__version__ = "0.1.2"

# Configuration variables
api_key = None
api_base = "https://portals.datawhys.ai/api/v0.2/"
api_v01_key = None
api_v01_base = "https://portals.datawhys.ai/api/v0.1/"

from datawhys_dashboard import api

from ._dashboards import create_dashboard
