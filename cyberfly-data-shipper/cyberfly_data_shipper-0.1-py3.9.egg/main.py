import json

from typing import Callable
import paho.mqtt.client as mqtt

from data_shipper import config, auth

mqttc = mqtt.Client(clean_session=True)


class CyberflyDataShipper:
    def __init__(self, device_id: str, key_pair: dict, network_id: str = "mainnet01"):
        self.key_pair = key_pair
        self.network_id = network_id
        self.device_data = {}
        self.device_id = device_id
        self.account = "k:" + self.key_pair.get("publicKey")
        self.caller = default_caller
        self.mqtt_client = mqttc
        self.topic = device_id
        self.mqtt_client.user_data_set(self)
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_received
        self.run(config.mqtt_broker, config.mqtt_port)

    def update_data(self, key: str, value):
        self.device_data.update({key: value})

    def on_message(self) -> Callable:
        def decorator(callback_function):
            self.caller = callback_function

        return decorator

    def run(self, host: str, port: int) -> None:
        try:
            self.mqtt_client.connect(
            host, port, 60)
        except Exception as e:
            print(e.__str__())
        self.mqtt_client.loop_start()


def on_connect(client: mqtt.Client, mqtt_class: CyberflyDataShipper, __flags, received_code: int) -> None:
    print("Connected with result code " + str(received_code))
    client.subscribe(mqtt_class.topic)


def on_received(__client: mqtt.Client, mqtt_class: CyberflyDataShipper, msg: mqtt.MQTTMessage) -> None:
    json_string = msg.payload.decode("utf-8")
    try:
        json_data = json.loads(json_string)
        if auth.validate_device_id(mqtt_class.device_id, json_data) and auth.check_auth(json_data, mqtt_class.network_id):
            try:
                mqtt_class.caller(json.loads(json_data['cmd'])['payload']['exec']['data']['device_exec'])
            except Exception as e:
                print(e.__str__())
        else:
            print("auth failed")
    except Exception as e:
        print(e.__str__())


def default_caller(data):
    pass
