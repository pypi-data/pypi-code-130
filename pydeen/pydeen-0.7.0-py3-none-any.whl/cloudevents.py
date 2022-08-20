"""
    Support for CloudEvent Messages - see the specs at https://cloudevents.io/
"""

import json
from datetime import datetime, timezone
import re
from tkinter import E
from pydeen.types import Base
from pydeen.service import ServiceAction, ServiceContext

class CloudEventMessage(Base):

    # standard cloud event attribvutes
    CE_SPEC                 = "specversion"
    CE_ID                   = "id"
    CE_TYPE                 = "type"
    CE_TIME                 = "time"
    CE_SOURCE               = "source"
    CE_SUBJECT              = "subject"
    CE_DATA                 = "data"
    CE_DATA_CONTENT_TYPE    = "datacontenttype"

    # custom attributes
    CEX_RECEIVERS           = "receivers"
    CEX_REPLY_TO            = "replyto"
    CEX_ANSWER_TO           = "answerto"

    # current spec support
    CE_MY_SPEC              = "1.0"

    # predefined content types
    CE_CONTENT_TYPE_JSON    = "application/json"
    CE_CONTENT_TYPE_XML     = "application/xml"
    CE_CONTENT_TYPE_TEXT    = "text"


    def __init__(self):
        super().__init__()
        self.type = "pydeen.CloudEventMessage"
        self.cex_prefix = "xba_"

    def get_property_x(self, name, default=None):
        return self.get_property(f"{self.cex_prefix}{name}", default)

    def set_property_x(self, name, value):
        self.get_property(f"{self.cex_prefix}{name}", value)

    def is_cloudevent_msg(self, msg:dict) -> bool:
        try:
            if msg == None or len(msg) == 0:
                return False

            json_keys   = msg.keys()
            if CloudEventMessage.CE_SPEC in json_keys \
                and CloudEventMessage.CE_TYPE in json_keys \
                and CloudEventMessage.CE_ID in json_keys \
                and CloudEventMessage.CE_DATA_CONTENT_TYPE in json_keys \
                and CloudEventMessage.CE_TIME in json_keys:
                self.trace(f"Cloudevent type {msg[CloudEventMessage.CE_TYPE]} spec {msg[CloudEventMessage.CE_SPEC]} detected")
                return True    
            else:
                self.trace(f"not an cloud event message object")
                return False

        except Exception as exc:
            self.trace(f"error while parsing cloud event message {type(exc)} - {exc}")
            return False                

    def is_cloudevent_payload(self, payload:str) -> bool:
        first_char = payload[0]
        if first_char == "{" or first_char == "[":
                try:
                    json_obj    = json.loads(payload)
                    return self.is_cloudevent_msg(json_obj)
                except Exception as exc:
                    self.trace(f"error while parsing cloud event message {type(exc)} - {exc}")
                    return False
        return False

    def set_from_payload(self, payload:str) -> bool:
        try:
            self._properties = json.loads(payload)
            return True
        except Exception as exc:
            self.error(f"error while setting cloud event message from string payload: {type(exc)} - {exc}")
            return False    

    def get_as_text(self):
        try:
            return json.dumps(self._properties)    
        except Exception as exc:
            self.error(f"errors while getting cloud event message {self._properties} as test: {type(exc)} - {exc}")    
            return None

    def get_ce_type(self) -> str:
        return self.get_property(CloudEventMessage.CE_TYPE)

    def get_ce_id(self) -> str:
        return self.get_property(CloudEventMessage.CE_ID)

    def get_ce_data_type(self) -> str:
        return self.get_property(CloudEventMessage.CE_DATA_CONTENT_TYPE)   

    def is_json_datatype(self) -> bool:
        datatype = self.get_ce_data_type()
        if datatype == None:
            return False
        else:
            if datatype == CloudEventMessage.CE_CONTENT_TYPE_JSON:
                return True, datatype
            else:
                return False, datatype    

    def get_my_ce_source(self,service:ServiceContext) -> str:
        return f"{service.type}::{service.get_client_id()}"
    
    def new_message(self, service:ServiceContext, ce_type:str):
        msg = CloudEventMessage()
        msg.debug = self.debug
        msg.interactive = self.interactive
        msg.set_property(CloudEventMessage.CE_SPEC, CloudEventMessage.CE_MY_SPEC)
        msg.set_property(CloudEventMessage.CE_ID, service.generate_UUID())
        msg.set_property(CloudEventMessage.CE_TYPE, ce_type) 
        msg.set_property(CloudEventMessage.CE_SOURCE, self.get_my_ce_source(service))  
        msg.set_property(CloudEventMessage.CE_TIME, datetime.now(timezone.utc).isoformat())
        return msg

    def set_receiver(self, receiver:list) -> bool:
        if receiver == None or len(receiver) == 0:
            return False
        else:
            self.set_property_x(CloudEventMessage.CEX_RECEIVERS, receiver)
            return True    

    def new_answer(self, service:ServiceContext, datatype:str=None, data_text:str=None, data_binary:bytes=None):
        # prepare new 
        answer = self.new_message(service, self.get_ce_type())
        if answer == None:
            self.error("wrong answer message context")
            return None

        # find old id
        old_id = self.get_ce_id()
        if old_id == None:
            self.error("no old message for answer messagge found")
            return None
        else:
            answer.set_property_x(CloudEventMessage.CEX_REPLY_TO, old_id)

        # find old sender
        old_sender = self.get_property_x(CloudEventMessage.CEX_ANSWER_TO)
        if old_sender != None:
            receiver = []
            receiver.append(old_sender)
            answer.set_receiver(receiver)

        return answer 

    def set_data_text(self, data:str, datatype:str=None):
        # set or detect datatype
        ce_datatype = datatype
        if ce_datatype == None and len(data) > 0:
            ce_datatype = CloudEventMessage.CE_CONTENT_TYPE_TEXT    
        
        # set properties
        self.set_property(CloudEventMessage.CE_DATA, data)
        self.set_property(CloudEventMessage.CE_DATA, ce_datatype)

    def set_data_json(self, data):
        # set properties
        self.set_property(CloudEventMessage.CE_DATA, data)
        self.set_property(CloudEventMessage.CE_DATA_CONTENT_TYPE, CloudEventMessage.CE_CONTENT_TYPE_JSON)

    def set_data_xml(self, data:str):
        # set properties
        self.set_property(CloudEventMessage.CE_DATA, data)
        self.set_property(CloudEventMessage.CE_DATA_CONTENT_TYPE, CloudEventMessage.CE_CONTENT_TYPE_XML)


class CloudEventTypeHandler(Base):
    def __init__(self):
        super().__init__()
        self.type = "pydeen.CloudEventMessage"

    def handle_cloud_event(self, msg:CloudEventMessage, service:ServiceContext)  -> bool:
        self.error("cloud event type handler - method handle_cloud_event not redefined. skip")
        return True  

    def send_answer_json(self, msg: CloudEventMessage, service:ServiceContext, data):
        answer = msg.new_answer(service)
        answer.set_data_json(data)
        answer_text = answer.get_as_text()
        return service.send_text(answer_text)            

class CloudEventServiceAction(ServiceAction):

    def __init__(self):
        super().__init__()
        self.type = "pydeen.ServiceActionCloudEvent"
        self.echo = False
        self.registered_types = {}

    def parse(self, payload) -> bool:
        # skip empty payload
        if payload == None or len(payload) < 2:
            return False
        
        # check format 
        ce_msg = CloudEventMessage()
        if ce_msg.is_cloudevent_payload(payload) == False:
            self.trace("payload is not a cloud event")
            return False
        else:
            return True


    def handle(self, payload, service:ServiceContext) -> bool:
        try:
            # prepare message
            ce_msg = CloudEventMessage()
            ce_msg.debug = self.debug
            ce_msg.interactive = self.interactive

            if ce_msg.set_from_payload(payload) == False:
                self.error("wrong cloud event payload")
                return False

            # get type and check valid message for this context    
            ce_type = ce_msg.get_ce_type()
            if ce_type == None:
                self.error("nocloud event type detected")
                return False

            # check my own message?
            ce_source = ce_msg.get_property(CloudEventMessage.CE_SOURCE)
            my_source = ce_msg.get_my_ce_source(service)
            if ce_source == my_source:
                self.trace("find my own message. skipped")
                return True

            # check receivers table
            receivers = ce_msg.get_property_x(CloudEventMessage.CEX_RECEIVERS)
            if receivers != None:
                receivers_str = str(receivers)
                if service.is_valid_client_id(receivers_str) == False:
                    self.trace(f"invalid receivers detected for cloud event message: {receivers_str}")
                    return True

            # call registered type handler
            return self.handle_cloud_event(ce_type, ce_msg, service)
        except Exception as exc:
            print(f"error while handling cloud event {type(exc)} - {exc}")
            self.error(f"error while handling cloud event {type(exc)} - {exc}")
            return False  

    def handle_cloud_event(self, ce_type, ce_msg:CloudEventMessage, service:ServiceContext) -> bool:
        try:
            # get handler
            handler = self.get_registered_type_handler(ce_type)
            if handler == None:
                self.trace(f"CloudActionType {ce_type} is not registered. Ignore.")
                return True

            # call handler
            return handler.handle_cloud_event(ce_msg, service)
        except Exception as exc:
            self.error(f"errors while processing cloud event type {ce_type}: {type(exc)} - {exc}")
            return False

    def is_type_registered(self, ce_type:str) -> bool:
        if self.registered_types == None or ce_type not in self.registered_types.keys():
            return False
        else:
            return True
    
    def register_type_handler(self, ce_type:str, handler:CloudEventTypeHandler):
        self.registered_types[ce_type] = handler

    def get_registered_type_handler(self, ce_type:str) -> CloudEventTypeHandler:
        try:
            if self.is_type_registered(ce_type) == False:
                return None
            else:    
                return self.registered_types[ce_type]
        except Exception as exc:
            self.error(f"Error while returning cloud event type handler for type {ce_type}: {type(exc)} - {exc}") 
            return None

