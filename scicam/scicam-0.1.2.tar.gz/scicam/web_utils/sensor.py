import json
import urllib.request
from socket import timeout as TimeoutException
import logging

logger = logging.getLogger(__name__)

class QuerySensor:
    def __init__(self, resource):
        self._resource = resource

    def query(self, timeout=1):
        url = f"http://{self._resource}"
        logger.debug(f"GET {url}")
        try:
            req = urllib.request.urlopen(url, timeout=timeout)
        except TimeoutException:
            logging.warning("Sensor timeout")
            return None
        except Exception:
            return None

        data_str = req.read().decode("utf-8")
        data = json.loads(data_str)
        data["temperature"] = float(data["temperature"])
        data["humidity"] = float(data["humidity"])
        return data

    def get_temperature(self):
        data = self.query()
        return data["temperature"]

    def get_humidity(self):
        data = self.query()
        return data["humidity"]


def setup(sensor):
    if sensor is None:
        sensor = None
    else:
        sensor = QuerySensor(sensor)
    return sensor
