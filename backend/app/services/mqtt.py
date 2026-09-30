import json
import os

import paho.mqtt.client as mqtt


class MQTTService:
    def __init__(self, on_message):
        self.host = os.getenv("MQTT_HOST", "localhost")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        self.topic = os.getenv("MQTT_TOPIC", "parking/slots")
        self.on_message = on_message
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            client.subscribe(self.topic)

    def _on_message(self, client, userdata, message):
        try:
            self.on_message(json.loads(message.payload.decode()))
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
            pass

    def start(self):
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            return True
        except Exception:
            return False

    def stop(self):
        self.client.loop_stop()
        try:
            self.client.disconnect()
        except Exception:
            pass

    def publish(self, payload: dict):
        return self.client.publish(self.topic, json.dumps(payload), qos=1)
