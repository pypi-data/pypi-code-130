# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2022
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

import os
from distutils.util import strtobool

class Environment():
    """
    Utility class to read environment variable values
    """

    def get_property_value(self, property_name, default=None):
        if os.environ and os.environ.get(property_name):
            return os.environ.get(property_name)
        return default

    def get_property_boolean_value(self, property_name, default=None):
        val = self.get_property_value(property_name, default=default)
        if val:
            try:
                return bool(strtobool(val))
            except ValueError:
                return False
        # return False for other values or None
        return False

    def is_iae_jobs_queuing_enabled(self):
        return self.get_property_boolean_value("ENABLE_IAE_JOBS_QUEUING", "false")
