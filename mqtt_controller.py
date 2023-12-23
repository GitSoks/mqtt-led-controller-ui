import paho.mqtt.client as mqtt
import json
from nicegui import ui

from device_manager import Device, DeviceManager


# Define MQTT topics
topic_main = "lightstrips"
topic_brodcast_command = topic_main + "/" + "cmd"
topic_state = topic_main + "/+/" + "sts"
topic_last_will = topic_main + "/+/" + "last-will"
topics = [topic_brodcast_command + "/" + str(i) for i in range(12)]
topics2 = topic_brodcast_command + "/" + "all"



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

    def connect_to_mqtt(self):
        self.client.username_pw_set(self.broker_username, self.broker_password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect

        ui.connect_button.props("loading=true")
        ui.status_label.text = "Connecting to MQTT broker..."

        try:
            self.client.connect(self.broker_address, self.broker_port)
            self.client.loop_start()
        except ConnectionRefusedError:
            print("MQTT connection refused")
            ui.status_label.text = "MQTT connection refused"
        except TimeoutError:
            print("MQTT connection timed out")
            ui.status_label.text = "MQTT connection timed out"
        except Exception as e:
            print("MQTT connection error:", str(e))
            ui.status_label.text = "MQTT connection error: " + str(e)
        else:
            ui.notify(
                "Connected to MQTT broker " + self.broker_address, type="positive"
            )

    def disconnect_from_mqtt(self):
        ui.status_label.text = "Disconnecting from MQTT broker..."
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker with result code " + str(rc))
        client.subscribe(topic_last_will)
        client.subscribe(topic_state)
        ui.status_label.text = "Connected to MQTT broker " + self.broker_address
        ui.connect_button.text = "Disconnect"
        ui.broker_address_textbox.enabled = False
        ui.broker_port_textbox.enabled = False
        ui.connect_button.props("color=negative")

    def on_message(self, client, userdata, msg):
        # print("Received message: " + msg.topic + " " + str(msg.payload))
        topic_parts = msg.topic.split("/")
        deviceId = topic_parts[1]
        print("Device ID:", deviceId)
        if topic_parts[2] == "sts":
            self.parse_json_message(msg.payload, self.device_manager.add_device(Device(deviceId, 12)))
        elif topic_parts[2] == "last-will":
            self.parse_last_will(msg.payload)

    def on_publish(self, client, userdata, mid):
        print("Message published")

    def on_disconnect(self, client, userdata, rc):
        ui.connect_button.text = "Connect"
        ui.status_label.text = "Disconnected from MQTT broker"
        print("Disconnected from MQTT broker")
        ui.broker_port_textbox.enabled = True
        ui.broker_address_textbox.enabled = True
        ui.connect_button.props("color=positive")
        ui.notify("Disconnected from MQTT broker", type="negative")


    def set_led_button_color(self, led_colors):
        for i, color in enumerate(led_colors):
            ui.led_buttons[i].style(f"color:{color}!important")

    def parse_json_message(self, json_message, device: Device):
        led_count = 0
        try:
            data = json.loads(json_message)
            lights = data.get("lights", {})
            for led_index, color_data in lights.items():
                red = color_data.get("red", 0)
                green = color_data.get("green", 0)
                blue = color_data.get("blue", 0)
                color_hex = "#{:02x}{:02x}{:02x}".format(red, green, blue)
                self.device_manager.devices[0].update_lights(int(led_index), color_hex)
                led_count += 1
        except json.JSONDecodeError:
            print("Invalid JSON message")
            
        self.set_led_button_color(self.device_manager.devices[0].lights)
        print("LED colors:", self.device_manager.devices[0].lights)
        print("LED count:", led_count)
        return self.device_manager.devices[0].lights, led_count

    def parse_last_will(self, msg_payload):
        if msg_payload.decode() == "offline":
            self.device_manager.devices[0].online = False
            ui.state_label.style("color:red")
            ui.state_label.text = "offline"
            
            # for i in range(len(ui.led_buttons)):
            #     ui.led_buttons[i].enabled = False
            # for i in range(len(ui.functions_buttons)):
            #     ui.functions_buttons[i].enabled = False            
            
        elif msg_payload.decode() == "online":
            self.device_manager.devices[0].online = True
            ui.state_label.style("color:green")
            ui.state_label.text = "online"
            
            # for i in range(len(ui.led_buttons)):
            #     ui.led_buttons[i].enabled = True
            # for i in range(len(ui.functions_buttons)):
            #     ui.functions_buttons[i].enabled = True            
            
        else:
            print("last will message not recognized")

    def send_color(self, device):
        payload = {"device-id": device.device_id, "lights": {}}
        for led_index, color in enumerate(self.device_manager.devices[0].lights):
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
