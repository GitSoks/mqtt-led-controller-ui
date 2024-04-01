import json
import logging
import time

import paho.mqtt.client as mqtt
from device_manager import Device, DeviceManager
from nicegui import ui

topic_main = "lightstrips"
topic_broadcast_command = topic_main + "/" + "cmd"
topic_state = topic_main + "/+/" + "sts"
topic_last_will = topic_main + "/+/" + "last-will"
topics = [topic_broadcast_command + "/" + str(i) for i in range(12)]
topics2 = topic_broadcast_command + "/" + "all"


class MQTTController:
    def __init__(
            self,
            broker_address: str,
            broker_port: int,
            broker_username: str,
            broker_password: str,
    ):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.broker_username = broker_username
        self.broker_password = broker_password
        self.client = mqtt.Client()
        self.device_manager = DeviceManager()

    @property
    def mqtt_connected(self):
        return self.client.is_connected()

    def connect_to_mqtt(self):
        self.client.username_pw_set(self.broker_username, self.broker_password)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        self.client.on_disconnect = self._on_disconnect

        try:
            self.client.connect(self.broker_address, self.broker_port)
            self.client.loop_start()
        except ConnectionRefusedError:
            logging.error("MQTT connection refused")
            return "MQTT connection refused"
        except TimeoutError:
            logging.error("MQTT connection timed out")
            return "MQTT connection timed out"
        except Exception as e:
            logging.error("MQTT connection error:", str(e))
            return "MQTT connection error: " + str(e)
        else:
            return "Connected to MQTT broker " + self.broker_address

    def disconnect_from_mqtt(self):
        self.client.loop_stop()
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, rc):
        logging.info("Connected to MQTT broker with result code " + str(rc))
        client.subscribe(topic_last_will)
        client.subscribe(topic_state)

        ui.status_label.text = "Connected to MQTT broker " + self.broker_address
        ui.broker_address_textbox.enabled = False
        ui.broker_port_textbox.enabled = False
        ui.connect_button.props("color=negative")

    def _on_message(self, client, userdata, msg):
        # logging.info("Received message: " + msg.topic + " " + str(msg.payload))
        _topic_parts = msg.topic.split("/")
        _device_id = _topic_parts[1]
        logging.info(f'Topic: {msg.topic}')
        logging.info(f'Device ID: {_device_id}')

        for _device_number, _device in enumerate(self.device_manager.devices):
            if _device_id == _device.device_id:
                break
        else:
            logging.info(f"New device found - adding {_device_id} to device manager")
            self.device_manager.add_device(Device(_device_id))
            _device_number = len(self.device_manager.devices) - 1
            _device = self.device_manager.devices[_device_number]

        if _topic_parts[2] == "sts":
            self.parse_json_message(msg.payload, _device)
        elif _topic_parts[2] == "last-will":
            self.parse_last_will(msg.payload, _device)

    def _on_publish(self, client, userdata, mid):
        logging.info("Message published")

    def _on_disconnect(self, client, userdata, rc):
        logging.info("Disconnected from MQTT broker")

        ui.status_label.text = "Disconnected from MQTT broker"

        ui.broker_port_textbox.enabled = True
        ui.broker_address_textbox.enabled = True

        for device in self.device_manager.devices:
            device.online = False

        ui.connect_button.props("color=positive")
        ui.notify("Disconnected from MQTT broker", type="negative")

    def parse_json_message(self, json_message, device: Device):
        led_count = 0
        try:
            data = json.loads(json_message)
            lights = data.get("lights", {})

            for led_index, color_data in lights.items():
                led_count += 1

            device.led_count = led_count    

            for led_index, color_data in lights.items():
                red = color_data.get("red", 0)
                green = color_data.get("green", 0)
                blue = color_data.get("blue", 0)
                color_hex = "#{:02x}{:02x}{:02x}".format(red, green, blue)
                device.update_lights(int(led_index), color_hex)
                try:
                    ui.led_buttons[device][int(led_index)].style(f"color:{color_hex}!important")           
                except IndexError:
                    logging.debug("Index out of range")
                except KeyError:
                    logging.debug("Key not found")

        except json.JSONDecodeError:
            logging.info("Invalid JSON message")

        logging.info(f'LED lights: {device.lights}')
        logging.info(f'LED count: {device.led_count}')
        return device.lights, led_count

    def parse_last_will(self, msg_payload, _device: Device):
        if msg_payload.decode() == "offline":
            _device.online = False

        elif msg_payload.decode() == "online":
            _device.online = True      

        else:
            logging.info("the last message is not recognized")

        logging.info(f'Online: {_device.online}')

    def send_color(self, device):
        payload = {"device-id": device.device_id, "lights": {}}
        for led_index, color in enumerate(device.lights):
            red, green, blue = (
                int(color[1:3], 16),
                int(color[3:5], 16),
                int(color[5:7], 16),
            )
            payload["lights"][str(led_index)] = {
                "red": red,
                "green": green,
                "blue": blue,
            }
        self.client.publish(
            topic_main + "/" + device.device_id + "/cmd",
            json.dumps(payload),
            retain=device.retain,
        )

    def delete_retained_messages(self, device):
        payload = ""
        self.client.publish(
            topic_main + "/" + device.device_id + "/cmd",
            json.dumps(payload),
            retain=True,
        )
        self.client.publish(
            topic_main + "/cmd",
            json.dumps(payload),
            retain=True,
        )

    def test_performance(self, device):

        # Start the performance timer
        start_time = time.time()



        # Send the color message
        self.send_color(device)

        # Wait for the device to change its light status
        while device.lights != device.target_lights:
            pass

        # Calculate the elapsed time
        elapsed_time = time.time() - start_time

        # Print the elapsed time
        print(f"Elapsed time: {elapsed_time} seconds")
