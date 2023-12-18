import paho.mqtt.client as mqtt
from nicegui import ui
import json
import time


from mqtt_controller import MQTTController
from device_manager import Device, DeviceManager




broker_address = "172.17.0.1"
broker_port = 1883
broker_username = "ui"
broker_password = "password"


mqtt_controller = MQTTController(
    broker_address, broker_port, broker_username, broker_password
)



device_manager= DeviceManager()

device = Device(device_id="device1", led_count=12)

device_manager.add_device(device)


mqtt_controller.device_manager.add_device(device)
mqtt_controller.device_manager.list_devices()


ui.colors(primary="#3785b2", secondary="blue")

ui.label("LED Controller UI").style(
    "color: #3785b2 ; font-size: 500%; font-weight: 900; bold: true;"
).props("text-uppercase")

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
    for Device in device_manager.devices:
        ui.tab(device.device_id, icon="online_prediction")
        
        
    

with ui.tab_panels(tabs, value=device_manager.devices[0].device_id) as panels:
    for Device in device_manager.devices:                
        with ui.tab_panel(Device.device_id):
            ui.functions_buttons = []
            ui.led_buttons = []

            with ui.row():
                with ui.switch(
                    text="Retain Light State",
                    value=device.retain,
                    on_change=lambda: (
                        setattr(device, "retain", retain_switch.value),
                        mqtt_controller.delete_retained_messages(device),
                    ),
                ) as retain_switch:
                    retain_switch.enabled = False
                    ui.functions_buttons.append(retain_switch)

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
                    button_all_off.enabled = False

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



for i in range(len(ui.led_buttons)):
    ui.led_buttons[i].enabled = False
for i in range(len(ui.functions_buttons)):
    ui.functions_buttons[i].enabled = False      




ui.run(
    dark=None,
    title="MQTT LED Controller",
    reload=True,
    native=False,
    favicon="💡",
)
