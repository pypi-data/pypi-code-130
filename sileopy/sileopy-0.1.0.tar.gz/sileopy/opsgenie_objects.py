# -*- coding: utf-8 -*-
"""
This method contains classes, methods and helper functions for Opsgenie
"""
# Python module imports
import opsgenie_sdk
import logging

# Local module imports
from sileopy.common_functions import tracelog


# Logger setup
logger = logging.getLogger(__name__)


class Opsgenie:
    """
    Main class for Opsgenie
    """
    @tracelog
    def __init__(self, key, host):
        self.conf = self.conf = opsgenie_sdk.configuration.Configuration()
        self.conf.api_key['Authorization'] = key
        self.conf.host = host

        self.api_client = opsgenie_sdk.api_client.ApiClient(configuration=self.conf)
        self.alert_api = opsgenie_sdk.AlertApi(api_client=self.api_client)
        self.heartbeat_api = opsgenie_sdk.HeartbeatApi(api_client=self.api_client)
        self.heartbeat_name = ''

    @tracelog
    def create_alert(
        self,
        alert_message,
        alert_description,
        alert_priority,
        alert_script_path,
        alert_script_hostname, 
        alert_alias = ''
        ):
        """
        Create an alert and send to Opsgenie

        Parameters
        ----------
        self : Opsgenie
            The object itself
        alert_message : String
            The message/subject of the alert
        alert_description : String
            The description of the alert
        alert_priority : String
            The priority of the alert (P1-P5)       
        alert_script_path : String
            The path to the script sending the alert
        alert_script_hostname : String
            The hostname or container ID running the script
        alert_alias : String
            The alias of the alert
            
        Returns
        -------
        -
        """
        body = opsgenie_sdk.CreateAlertPayload(
            message=alert_message,
            description=alert_description or '',
            details={
                'Alert script path': alert_script_path \
                    or '</path/to/alert script>',
                'Alert script hostname / container ID': alert_script_hostname \
                    or '<name of host or ID of container running the alert script>'
            },
            priority=alert_priority, 
            alias=alert_alias or ''
        )
        logger.debug('create_alert body: \n%s', body)
        try:
            response = self.alert_api.create_alert(create_alert_payload=body)
            logger.info(response)
            return response
        except opsgenie_sdk.ApiException as err:
            logger.error(
                "Exception when calling AlertApi->create_alert: %s\n" % err
            )
    
    @tracelog
    def create_heartbeat_ping(self):
        """
        Create a heartbeat and send to Opsgenie

        Parameters
        ----------
        self : Opsgenie
            The object itself

        Returns
        -------
        -
        """
        try:
            logger.debug('Sending ping to heartbeat name: %s', self.heartbeat_name)
            ping_response = self.heartbeat_api.ping(self.heartbeat_name)
            logger.info(ping_response)
            return ping_response
        except opsgenie_sdk.ApiException as err:
            logger.error("Exception when calling HeartBeatApi->ping: %s\n" % err)
