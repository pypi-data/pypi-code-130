"""
// ========================================================================
// Copyright (c) 2018-2019 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""

__author__ = "Rashtrapathy"
__copyright__ = "Copyright (c) 2018-2019 by Iotium, Inc."
__license__ = "All rights reserved."
__email__ = "rashtrapathy.c@iotium.io"

import iotiumlib.models.service_listener_creation_vo
from iotiumlib.models import service_ports_vo, service_listener_update_vo, service_selector_vo
from iotiumlib.requires.commonWrapper import *
from iotiumlib.requires.resourcePayload import *

serviceId = str()
orgId = str()


class service(object):
    """
    Service Resource
    """

    def __init__(self, action, payload=None, service_id=None, template_id=None, filters=None):

        if payload is None:
            payload = {}

        def add_service(uri):
            return service.Service(self, method='post', uri=uri)

        def edit_service(uri):
            return service.Service(self, method='put', uri=uri)

        def delete_service(uri):
            return service.Service(self, method='delete', uri=uri)

        def get_service(uri):
            return service.Service(self, method='get', uri=uri)

        def getv2_service(uri):
            return service.Service(self, method='getv2', uri=uri, filters=filters)

        def getv2_template_service(uri):
            return service.Template(self, method='getv2', uri=uri)

        def get_template_service(uri):
            return service.Template(self, method='get', uri=uri)

        def get_service_id_service(uri):
            return service.Service(self, method='get', uri=uri)

        def restart_service(uri):
            return service.Service(self, method='post', uri=uri)

        _function_mapping = {
            'add': add_service,
            'edit': edit_service,
            'delete': delete_service,
            'get': get_service,
            'get_service_id': get_service_id_service,
            'getv2_template': getv2_template_service,
            'get_template': get_template_service,
            'getv2': getv2_service,
            'restart': restart_service

        }

        self.uri = {
            add_service: 'api/v1/service',
            get_service: 'api/v1/service',
            edit_service: 'api/v1/service/{serviceId}',
            delete_service: 'api/v1/service/{serviceId}',
            get_service_id_service: 'api/v1/service/{serviceId}',
            getv2_service: 'api/v2/service',
            getv2_template_service: 'api/v2/servicetemplate',
            get_template_service: 'api/v1/servicetemplate/{templateId}',
            restart_service: 'api/v1/service/{serviceId}/restart'
        }

        # self.payload = resourcePaylod.Service(payload).__dict__
        self.payload = payload

        self.serviceId = service_id
        self.templateId = template_id

        self.orgId = orch.id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_service'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def __del__(self):
        self.payload = dict()
        self.Response = Response()

    def Service(self, method, uri, filters=None):

        respOp = dict()
        paramRequired = checkforUriParam(uri)
        if paramRequired:
            for param in paramRequired:
                uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)

        if method == 'get':
            respOp = getApi(formUri(uri))
        elif method == 'getv2':
            self.Response = getApiv2(formUri(uri), filters)
            return self.Response
        elif method == 'post':
            respOp = postApi(formUri(uri), self.payload)
        elif method == 'put':
            respOp = putApi(formUri(uri), self.payload)
        elif method == 'delete':
            respOp = deleteApi(formUri(uri))
        else:
            return self.Response
        self.Response.output = respOp.json()
        self.Response.code = respOp.status_code
        return self.Response

    def Template(self, method, uri, filters=None):

        respOp = dict()
        paramRequired = checkforUriParam(uri)
        if paramRequired:
            for param in paramRequired:
                uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)

        if method == 'get':
            respOp = getApi(formUri(uri))
        elif method == 'getv2':
            self.Response = getApiv2(formUri(uri), filters)
            return self.Response
        elif method == 'post':
            respOp = postApi(formUri(uri), self.payload)
        elif method == 'put':
            respOp = putApi(formUri(uri), self.payload)
        elif method == 'delete':
            respOp = deleteApi(formUri(uri))
        else:
            return self.Response
        self.Response.output = respOp.json()
        self.Response.code = respOp.status_code
        return self.Response

    @staticmethod
    def delete(service_id):
        return service(action='delete', service_id=service_id)

    @staticmethod
    def get(service_id=None, template_id=None):
        if service_id is not None:
            return service(action='get_service_id', service_id=service_id)
        elif template_id is not None:
            return service(action='get_template', template_id=template_id)
        else:
            return service(action='get')

    @staticmethod
    def getv2(filters=None):
        return service(action='getv2', filters=filters)

    @staticmethod
    def getv2_template(filters=None):
        return service(action='getv2_template', filters=filters)

    @staticmethod
    def add(payload):
        return service(action="add", payload=payload)

    @staticmethod
    def edit(service_id, payload):
        return service(action="edit", payload=payload, service_id=service_id)

    @staticmethod
    def restart(service_id):
        return service(action="restart", service_id=service_id)

    class listener(object):
        def __init__(self, action, payload=None, listener_id=None, filters=None, service_id=None, node_id=None):
            if payload is None:
                payload = {}

            def add_listener(uri):
                return service.listener.service_listener(self, method='post', uri=uri)

            def delete_listener(uri):
                return service.listener.service_listener(self, method='delete', uri=uri)

            def edit_listener(uri):
                return service.listener.service_listener(self, method='put', uri=uri)

            def get_listener(uri):
                return service.listener.service_listener(self, method='get', uri=uri)

            def getv2_listener(uri):
                return service.listener.service_listener(self, method='getv2', uri=uri, filters=filters)

            _function_mapping = {
                'get': get_listener,
                'getv2': getv2_listener,
                'add': add_listener,
                'edit': edit_listener,
                'delete': delete_listener
            }

            self.uri = {
                get_listener: 'api/v1/listener/{listenerId}',
                getv2_listener: 'api/v2/listener',
                add_listener: 'api/v1/listener',
                edit_listener: 'api/v1/listener/{listenerId}',
                delete_listener: 'api/v1/listener/{listenerId}'
            }

            self.payload = payload
            self.orgId = orch.id
            self.nodeId = node_id
            self.serviceId = service_id
            self.listenerId = listener_id
            self.Response = Response()

            _wrapper_fun = _function_mapping[action]
            args = '{}_listener'.format(action)
            _wrapper_fun(self.uri[eval(args)])

        def __del__(self):
            self.payload = dict()
            self.Response = Response()

        def service_listener(self, method, uri, filters=None):
            paramRequired = checkforUriParam(uri)
            if paramRequired:
                for param in paramRequired:
                    uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)
            if method == 'get':
                respOp = getApi(formUri(uri))
            elif method == 'getv2':
                self.Response = getApiv2(formUri(uri), filters)
                return self.Response
            elif method == 'post':
                respOp = postApi(formUri(uri), self.payload)
            elif method == 'put':
                respOp = putApi(formUri(uri), self.payload)
            elif method == 'delete':
                respOp = deleteApi(formUri(uri))
            else:
                return self.Response
            self.Response.output = respOp.json()
            self.Response.code = respOp.status_code
            return self.Response

        @staticmethod
        def add(name, type, node_id, service_name, service_ports, allow_access_from=None, org_id=None, metadata=None):
            ports = list()
            sn = iotiumlib.models.service_selector_vo.ServiceSelectorVO(name=service_name)
            for p in service_ports:
                ports.append(iotiumlib.models.service_ports_vo.ServicePortsVO(p['protocol'], p['port'], p['node_port']))

            body = iotiumlib.models.service_listener_creation_vo.ServiceListenerCreationVO(name=name,
                                                                                           type=type,
                                                                                           node_id=node_id,
                                                                                           service_selector=sn,
                                                                                           allow_access_from=allow_access_from,
                                                                                           service_ports=ports)
            return service.listener(action="add", payload=body.to_dict())

        @staticmethod
        def edit(listener_id, name=None, allow_access_from=None, service_ports=None):
            ports = list()
            if service_ports is not None:
                for p in service_ports:
                    ports.append(iotiumlib.models.service_ports_vo.ServicePortsVO(p['protocol'],
                                                                                  p['port'],
                                                                                  p['node_port']))

            body = iotiumlib.models.service_listener_update_vo.ServiceListenerUpdateVO(name=name,
                                                                                       allow_access_from=allow_access_from,
                                                                                       service_ports=ports)
            return service.listener(action="edit", listener_id=listener_id, payload=body.to_dict())

        @staticmethod
        def delete(listener_id):
            return service.listener(action="delete", listener_id=listener_id)

        @staticmethod
        def get(listener_id):
            return service.listener(action='get', listener_id=listener_id)

        @staticmethod
        def getv2(filters=None):
            return service.listener(action='getv2', filters=filters)
