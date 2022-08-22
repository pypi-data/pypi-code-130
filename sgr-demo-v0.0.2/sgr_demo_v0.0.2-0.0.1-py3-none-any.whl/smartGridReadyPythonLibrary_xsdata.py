import time
import os
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.context import XmlContext

# Import generated Data Classes
from data_classes.ei_rest_api import SgrRestapideviceDescriptionType
from data_classes.ei_modbus import SgrModbusDeviceDescriptionType

# Smartgrid Ready Libraries
from datetime import datetime, timezone
import jmespath
from EI4_RestAPI_xsdata import EI4RestAPI
from jinja2 import Template


interface_file = 'SGr_04_0018_CLEMAP_EIcloudEnergyMonitorV0.2.1.xml'
parser = XmlParser(context=XmlContext())
root = parser.parse(interface_file, SgrRestapideviceDescriptionType)

#print(root2)

class GenericInterface():

    def __init__(self, xmlSGrInterfaceFile, private_config):
        self.private_config = private_config
        self.communication_channel = EI4RestAPI(root, private_config)
        self.packet = False
        self.cycle_start_timestamp = time.time()
        self.receivedAt = time.time()

    
    def add_private_config(self, string, params) -> str: 
        """
        Auxiliary function that adds te sensor_id number to the following string: "/digitaltwins/{{sensor_id}}"
        """
        jT = Template(string)
        private_config = jT.render(params['RESSOURCE'])
        return private_config

    
    def new_packet(self, private_config, communication_channel, endpoint) -> tuple:
        """
        Function that loads a new packet from the communication_channel with the api
        :return: (packet, recieved)
        """
        endpoint = self.add_private_config(endpoint, private_config) # Adds sensor_id to the private config   
        packet = communication_channel.get(endpoint)
        recieved = time.time()
        recievedAt = datetime.fromtimestamp(recieved, timezone.utc)
        return(packet, recieved)

    # get_val function to implement for getting a single value
    def get_val(self, FP_Name, DP_Name) -> float:
        """
        :return: Datapoint value
        """

        for fp in root.fp_list_element:
            if fp.functional_profile.profile_name == FP_Name:
                for dp in fp.dp_list_element:
                    if dp.data_point[0].datapoint_name == DP_Name:
                        # If there is no packet or it is older than 10 seconds, we get a new one
                        if not self.packet or self.cycle_start_timestamp - self.receivedAt > 10.0:        
                            endpoint = dp.rest_apidata_point[0].rest_apiend_point
                            self.packet, self.receivedAt = self.new_packet(self.private_config, self.communication_channel, endpoint)
                        # We get the datapoint's information
                        value = jmespath.search(dp.rest_apidata_point[0].rest_apijmespath, self.packet) # Returns the key value in the jmes packet
                        unit = dp.data_point[0].unit.value
                        timestamp = time.ctime(self.receivedAt)
                        aged = self.cycle_start_timestamp - self.receivedAt
                        print(f"FP {FP_Name} DP {DP_Name} value {value} {unit} received at {timestamp} aged {aged :.2f} seconds")
                        return