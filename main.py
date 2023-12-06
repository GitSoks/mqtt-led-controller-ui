import paho.mqtt.client as mqtt
from nicegui import ui
import json
import time

# Define MQTT topics
topic_main = "lightstrips"
topic_brodcast_command = topic_main + "/" + "cmd"
topic_state = topic_main + "/+/" + "sts"
topic_last_will = topic_main + "/+/" + "last-will"
topics = [topic_brodcast_command + "/" + str(i) for i in range(12)]
topics2 = topic_brodcast_command + "/" + "all"

broker_address = "172.17.0.1"
broker_port = 1883
broker_username = "ui"
broker_password = "password"


class Device:
    def __init__(self, device_id: str, led_count: int):
        self.device_id = device_id
        self._online = False
        self.led_count = led_count
        self.lights = [str(i) for i in range(led_count)]
        self._online_change_event = None
        self.retain = True

    @property
    def online(self):
        return self._online

    @online.setter
    def online(self, status: bool):
        if self._online != status:
            self._online = status
            if self._online_change_event is not None:
                self._online_change_event(status)

    def update_lights(self, index: int, color: str):
        self.lights[index] = color

    def set_online_change_event(self, event):
        self._online_change_event = event


class DeviceManager:
    def __init__(self):
        self.devices = []

    def add_device(self, device: Device):
        self.devices.append(device)

    def list_devices(self):
        for device in self.devices:
            print(
                f"Device ID: {device.device_id}, Online: {device.online}, Lights: {device.lights}"
            )

    def get_online_devices(self):
        return [device for device in self.devices if device.online]


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
        for i in range(len(ui.led_buttons)):
            ui.led_buttons[i].enabled = True
        for i in range(len(ui.functions_buttons)):
            ui.functions_buttons[i].enabled = True

    def on_message(self, client, userdata, msg):
        # print("Received message: " + msg.topic + " " + str(msg.payload))
        topic_parts = msg.topic.split("/")
        deviceId = topic_parts[1]
        print("Device ID:", deviceId)
        if topic_parts[2] == "sts":
            self.parse_json_message(msg.payload)
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
        for i in range(len(ui.led_buttons)):
            ui.led_buttons[i].enabled = False

        for i in range(len(ui.functions_buttons)):
            ui.functions_buttons[i].enabled = False

    def set_led_button_color(self, led_colors):
        for i, color in enumerate(led_colors):
            ui.led_buttons[i].style(f"color:{color}!important")

    def parse_json_message(self, json_message):
        led_count = 0
        try:
            data = json.loads(json_message)
            lights = data.get("lights", {})
            for led_index, color_data in lights.items():
                red = color_data.get("red", 0)
                green = color_data.get("green", 0)
                blue = color_data.get("blue", 0)
                color_hex = "#{:02x}{:02x}{:02x}".format(red, green, blue)
                device.update_lights(int(led_index), color_hex)
                led_count += 1
        except json.JSONDecodeError:
            print("Invalid JSON message")
        self.set_led_button_color(device.lights)
        print("LED colors:", device.lights)
        print("LED count:", led_count)
        return device.lights, led_count

    def parse_last_will(self, msg_payload):
        if msg_payload.decode() == "offline":
            device.online = False
            ui.state_label.style("color:red")
            ui.state_label.text = "offline"
        elif msg_payload.decode() == "online":
            device.online = True
            ui.state_label.style("color:green")
            ui.state_label.text = "online"
        else:
            print("last will message not recognized")

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


mqtt_controller = MQTTController(
    broker_address, broker_port, broker_username, broker_password
)

device = Device(device_id="device1", led_count=12)
mqtt_controller.device_manager.add_device(device)
mqtt_controller.device_manager.list_devices()


ui.colors(primary="#3785b2", secondary="blue")

ui.label("LED Controller UI").style(
    "color: #ffff ; font-size: 400%; font-weight: 700; bold: true;"
)
ui.label("provided by David Sokolowski").style(
    "color: #ffff ; font-size: 100%; font-weight: 0; bold: false;position: relative;bottom: 30px;right: 0px;"
)

with ui.card():
    ui.status_label = ui.label(text="Connecting to MQTT broker...")
    ui.connect_button = ui.button(
        text="Connect",
        on_click=lambda: mqtt_controller.connect_to_mqtt()
        if not mqtt_controller.client.is_connected()
        else mqtt_controller.disconnect_from_mqtt(),
    )
    with ui.row():
        ui.broker_address_textbox = ui.input(
            label="MQTT Broker Address",
            value=broker_address,
            placeholder="IP format: 172.17.0.1",
            autocomplete=["172.17.0.1", "192.168.1.10"],
            on_change=lambda: mqtt_controller.set_ip_value(),
        )
        ui.broker_port_textbox = ui.number(
            label="MQTT Broker Port",
            value=broker_port,
            placeholder="default: 1883",
            format="%.0f",
            on_change=lambda: mqtt_controller.set_port_value(),
        )


def set_ip_value():
    global broker_address
    broker_address = ui.broker_address_textbox.value


def set_port_value():
    global broker_port
    broker_port = int(ui.broker_port_textbox.value)


def rotating_led_animation(device, mqtt_controller):
    colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#800080", "#00FFFF"]
    duration = 0.4  # Duration in seconds for each color
    rotations = 3  # Number of rotations

    for y in range(rotations):
        for i in range(device.led_count):
            color = colors[y]
            device.update_lights(i, color)
            mqtt_controller.send_color(device)
            time.sleep(duration)
        for i in range(device.led_count):
            color = "#000000"
            device.update_lights(i, color)
            mqtt_controller.send_color(device)
            time.sleep(duration)

    for _ in range(rotations):
        for i in range(device.led_count):
            for j in range(device.led_count):
                device.update_lights(j, "#000000")
            color = colors[i % len(colors)]
            device.update_lights(i, color)
            mqtt_controller.send_color(device)
            time.sleep(duration)

    for _ in range(device.led_count):
        device.update_lights(j, "#000000")
        mqtt_controller.send_color(device)


mqtt_controller.connect_to_mqtt()

with ui.tabs() as tabs:
    tab_1 = ui.tab("Controller 1", icon="online_prediction")
    tab_2 = ui.tab("Controller 2", icon="online_prediction")
    tab_3 = ui.tab("Controller 3", icon="online_prediction")

with ui.tab_panels(tabs, value=tab_1) as panels:
    with ui.tab_panel(tab_1):
        ui.functions_buttons = []
        ui.led_buttons = []

        with ui.row():
            ui.retain_switch = ui.switch(
                text="Retain Light State",
                value=device.retain,
                on_change=lambda: (
                    setattr(device, "retain", ui.retain_switch.value),
                    mqtt_controller.delete_retained_messages(device),
                ),
            )
            ui.state_label = ui.label("offline").style(
                "right: -210px;top: -10px;position: relative; color:red;"
            )

        with ui.grid(columns=3):
            with ui.button(
                text="all Lights off",
                icon="blur_off",
                on_click=lambda: (
                    [
                        device.update_lights(i, "#000000")
                        for i in range(device.led_count)
                    ],
                    mqtt_controller.send_color(device),
                ),
            ).props("stack glossy") as button_all_off:
                ui.functions_buttons.append(button_all_off)

            with ui.button(icon="palette").props("stack glossy") as button_all:
                button_all.enabled = False
                button_all.text = "All Lights"
                ui.color_picker(
                    on_pick=lambda e: (
                        [
                            device.update_lights(i, e.color)
                            for i in range(device.led_count)
                        ],
                        mqtt_controller.send_color(device),
                    ),
                )
                ui.functions_buttons.append(button_all)
            with ui.button(
                text="Animation",
                icon="animation",
                on_click=lambda: (
                    [rotating_led_animation(device, mqtt_controller)],
                    mqtt_controller.send_color(device),
                ),
            ).props("stack glossy") as button_animation:
                ui.functions_buttons.append(button_animation)
                button_animation.enabled = False

            for i in range(12):
                button_name = "button" + str(i)
                with ui.button(icon="lightbulb") as button:
                    button.enabled = False
                    button.name = button_name
                    button.text = "Light " + str(i)
                    color = ui.color_picker(
                        on_pick=lambda e, led_index=i, button=button: (
                            device.update_lights(led_index, e.color),
                            mqtt_controller.send_color(device),
                        )
                    )
                    ui.led_buttons.append(button)


ui.run(
    dark=None,
    title="MQTT LED Controller",
    reload=True,
    native=False,
    favicon="💡",
)
