from ontopia_py.iot.MonitoringFacility import MonitoringFacility
from ..ns import *
from .MonitoringFacility import MonitoringFacility


class Actuator(MonitoringFacility):
    __type__ = IOT["Actuator"]
