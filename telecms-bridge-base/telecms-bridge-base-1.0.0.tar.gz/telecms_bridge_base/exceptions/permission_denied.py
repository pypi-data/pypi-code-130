from telecms_bridge_base import status
from telecms_bridge_base.exceptions.api import APIException


class PermissionDenied(APIException):
    default_detail = 'Permission denied'
    default_code = 'permission_denied'
    default_status_code = status.HTTP_403_FORBIDDEN
