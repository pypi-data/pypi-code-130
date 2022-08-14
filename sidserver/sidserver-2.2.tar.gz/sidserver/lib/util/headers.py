from sidserver.lib.util import device, signature

from uuid import uuid4

sid = None

class ApisHeaders:
    def __init__(self, data = None, type = None, deviceId: str = None, sig: str = None):
        if deviceId:
            dev = device.DeviceGenerator(deviceId=deviceId)
        else:
            dev = device.DeviceGenerator()

        headers = {
            "NDCDEVICEID": dev.device_id,
            "Accept-Language": "en-US",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": dev.user_agent,
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "Upgrade"
        }

        if data:
            headers["Content-Length"] = str(len(data))
            headers["NDC-MSG-SIG"] = signature(data)
        if sid: headers["NDCAUTH"] = f"sid={sid}"
        if type: headers["Content-Type"] = type
        if sig: headers["NDC-MSG-SIG"] = sig

        self.headers = headers

