from nicegui import ui
import os
import random

from mqtt_controller import MQTTController
from device_manager import Device
from ui_elements import ui_title, ui_connection_control, ui_panels


from settings import broker_address, broker_port, broker_username, broker_password, test_devices


import logging
import coloredlogs

coloredlogs.install(level='Info')

if test_devices:
    device_test_1 = Device(device_id="test1")
    device_test_2 = Device(device_id="test2")
    device_test_3 = Device(device_id="test3")

    device_test_1.led_count = 6
    
    device_test_2.led_count = 2
    device_test_2.lights = ["red", "green"]
    
    device_test_3.led_count = 12
    for device_test_3_led in range(device_test_3.led_count):
        color = random.choice(["red", "green", "blue"])
        device_test_3.lights[device_test_3_led ]= color
    

    ui.timer(4.0, lambda: setattr(device_test_3, "online", True), once=True)
    ui.timer(15.0, lambda: setattr(device_test_2, "online", True), once=True)


def main():
    os.system('cls')  # clear screen

    mqtt_controller = MQTTController(
        broker_address, broker_port, broker_username, broker_password
    )

    mqtt_controller.connect_to_mqtt()

    if test_devices:
        mqtt_controller.device_manager.add_device(device_test_1)
        mqtt_controller.device_manager.add_device(device_test_2)
        mqtt_controller.device_manager.add_device(device_test_3)

    for device in mqtt_controller.device_manager.devices:
        device.online = False

    mqtt_controller.device_manager.list_devices()

    ui.colors(primary="#3785b2", secondary="blue")

    ui.status_label = ui.element()
    ui.connect_button = ui.element()

    ui_title()
    ui_connection_control(mqtt_controller)
    ui_panels(mqtt_controller)

    ui.timer(600.0, lambda: ui_panels.refresh(),)

    ui.run(
        dark=None,
        title="MQTT LED Controller",
        reload=True,
        native=False,
        port=80,
        favicon="💡",
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
