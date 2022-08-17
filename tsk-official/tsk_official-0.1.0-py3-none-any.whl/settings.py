from configparser import ConfigParser
from datetime import datetime, timedelta
import os

from tsk import utils


class Settings(ConfigParser):
    """Models the settings for tsk."""

    def __init__(self):
        super().__init__(allow_no_value=True)
        self.conf_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        self.read(self.conf_path)

    def commit(self):
        """Commit settings changes."""
        with open(self.conf_path, 'w') as configfile:
            self.write(configfile)

    def get_default_val(self, key: str):
        """Get a default value from TaskDefaults."""
        
        if key == 'date_due':
            num_days_due = self.getint('TaskDefaults', 'date_due')
            if num_days_due == -1:
                return None
            return utils.tstamp_to_american_datestr(
                datetime.now().date()
                + timedelta(days=num_days_due)
            )
