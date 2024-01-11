import logging
import asyncio
import functools
from nicegui import ui,events, app

from device_manager import Device
from mqtt_controller import MQTTController
from settings import broker_address, broker_port, led_ring_12_image_path


app.on_connect(lambda: on_ui_client_connect())

def on_ui_client_connect():
    logging.info("Client connected")
    ui.notify("Client connected", type="positive", color="teal")
    ui_panels.refresh()


def ui_title() -> None:
    ui.label("LED Controller UI").style(
        "color: #3785b2 ; font-size: 500%; font-weight: 900; bold: true;"
    ).props("text-uppercase")

    ui.label("made by David Sokolowski").style(
        "color: #ffff ; font-size: 100%; font-weight: 0; bold: false; position: relative; bottom: 30px;right: 0px;"
    )

def toggle_mqtt_connection(mqtt_controller: MQTTController) -> None:
    if not mqtt_controller.client.is_connected():
        ui.status_label.text = "Connecting to MQTT broker…"
        _connection_state = mqtt_controller.connect_to_mqtt()
        ui.status_label.text = _connection_state
        if _connection_state.startswith("Connected"):
            ui.notify(
                _connection_state, type="positive"
            )
        ui.timer(1.0, lambda: ui_panels.refresh(), once=True)

    else:
        mqtt_controller.disconnect_from_mqtt()
        ui.timer(1.0, lambda: ui_panels.refresh(), once=True)


def ui_connection_control(mqtt_controller: MQTTController) -> None:
    with ui.card():
        ui.status_label = ui.label(text="Connecting to MQTT broker…")
        with ui.button(
            text="Connect",
            on_click=lambda: toggle_mqtt_connection(mqtt_controller),
            color= "positive",
        ) as ui.connect_button:
            ui.connect_button.bind_text_from(mqtt_controller, "mqtt_connected", lambda e: "Disconnect" if e else "Connect")
            
        with ui.row():
            ui.broker_address_textbox = ui.input(
                label="MQTT Broker Address",
                value=broker_address,
                placeholder="IP format: 172.17.0.1",
                autocomplete=["172.17.0.1", "192.168.1.10"],
                on_change=lambda: set_ip_value(mqtt_controller),
            )
            ui.broker_port_textbox = ui.number(
                label="MQTT Broker Port",
                value=broker_port,
                placeholder="default: 1883",
                format="%.0f",
                on_change=lambda: set_port_value(mqtt_controller),
            )

def set_ip_value(mqtt_controller: MQTTController):
    mqtt_controller.broker_address = ui.broker_address_textbox.value

def set_port_value(mqtt_controller: MQTTController):
    mqtt_controller.broker_port = int(ui.broker_port_textbox.value)

async def rotating_led_animation(mqtt_controller: MQTTController, device: Device):
    colors = ["#FF0000", "#00FF00", "#0000FF",
                "#FFFF00", "#800080", "#00FFFF"]
    duration = 0.4  # Duration in seconds for each color
    rotations = 3  # Amount rotations
    
    for _ in range(rotations):
        for _currentLight in range(device.led_count):
            for _ in range(device.led_count):
                device.update_lights(_, "#000000")
            _color = colors[_currentLight % len(colors)]
            device.update_lights(_currentLight, _color)
            mqtt_controller.send_color(device)
            await asyncio.sleep(duration)
            
    for _cycles in range(rotations):
        for _currentLight in range(device.led_count):
            _color = colors[_cycles]
            device.update_lights(_currentLight, _color)
            mqtt_controller.send_color(device)
            await asyncio.sleep(duration)
        for _currentLight in range(device.led_count):
            device.update_lights(_currentLight, "#000000")
            mqtt_controller.send_color(device)
            await asyncio.sleep(duration)



    for _ in range(device.led_count):
        device.update_lights(_, "#000000")
        mqtt_controller.send_color(device)



@ui.refreshable
def ui_panels(mqtt_controller: MQTTController) -> None:
    with ui.tabs() as tabs:
        for _current_device in mqtt_controller.device_manager.devices:
            if _current_device.device_id.startswith("test"):
                ui.tab(_current_device.device_id, icon="science")
            else:
                ui.tab(_current_device.device_id, icon="online_prediction")

    with ui.tab_panels(tabs, value=mqtt_controller.device_manager.selected_device,
                        on_change=lambda e: (
                                setattr(mqtt_controller.device_manager, "selected_device", e.value),)):
        
        
        ui.led_buttons = {mqtt_controller.device_manager.devices[i]: [] for i in range(len(mqtt_controller.device_manager.devices))}
        for _current_tab, _current_device in enumerate(mqtt_controller.device_manager.devices):
            ui.functions_buttons = []

            
            with ui.tab_panel(_current_device.device_id):
                with ui.row():
                    with ui.switch(
                            text="Retain Light State",
                            value=_current_device.retain,
                            on_change=lambda: (
                                    setattr(_current_device, "retain", retain_switch.value),
                                    mqtt_controller.delete_retained_messages(_current_device),
                            ),
                    ).style(
                        "right: 0px;top: 0px;position: relative; "
                    ) as retain_switch:
                        retain_switch.enabled = False
                        retain_switch.bind_enabled_from(_current_device, "online")
                        ui.functions_buttons.append(retain_switch)
                        
                    with ui.label(
                        text='Amount of Lights',
                    ).style("right: -210px; top: 10px;position: relative; font-size: 100%;") as led_count_label:
                        led_count_label.bind_text_from(_current_device, "led_count", lambda e: f"{e} lights")
                        led_count_label.enabled = False
                    
                
                    class state_label(ui.label):
                        
                        def _handle_text_change(self, text: str) -> None:

                            
                            if text == 'online':
                                self.classes(replace='text-positive')                  
                                #if mqtt_controller.mqtt_connected:
                                #    ui.notify(f'{_current_device.device_id} online', type="positive", color='teal')      
                            elif text == 'offline':
                                self.classes(replace='text-negative')
                                #if mqtt_controller.mqtt_connected:
                                #    ui.notify(f'{_current_device.device_id} offline', type="negative", color="orange")
                            super()._handle_text_change(text)            

                    with  state_label(" ").style(
                        "right: -150px;top: -15px;position: relative; font-size: 120%;"
                    ) as ui.online_state_label:
                        ui.online_state_label.bind_text_from(_current_device, "online", lambda e: "online" if e else "offline")
                        ui.online_state_label.bind_visibility_from(target_object=mqtt_controller ,target_name= "mqtt_connected", value=True)

                with ui.grid(columns=3):
                    with ui.button(
                            text="all Lights off",
                            icon="blur_off",
                            on_click=lambda: (
                                    [
                                        _current_device.update_lights(_, "#000000")
                                        for _ in range(_current_device.led_count)
                                    ],
                                    mqtt_controller.send_color(_current_device),
                            ),
                    ).props("stack glossy") as button_all_off:
                        ui.functions_buttons.append(button_all_off)
                        button_all_off.enabled = False
                        button_all_off.bind_enabled_from(_current_device, "online")

                    with ui.button(icon="palette").props("stack glossy") as button_all:
                        button_all.enabled = False
                        button_all.text = "All Lights"
                        ui.color_picker(
                            on_pick=lambda e: (
                                [
                                    _current_device.update_lights(_, e.color)
                                    for _ in range(_current_device.led_count)
                                ],
                                mqtt_controller.send_color(_current_device),
                            ),
                        )
                        ui.functions_buttons.append(button_all)
                        button_all.bind_enabled_from(_current_device, "online")
                        
                    with ui.button(
                            text="Animation",
                            icon="animation",
                            on_click=functools.partial(rotating_led_animation,mqtt_controller,_current_device)
                    ).props("stack glossy") as button_animation:
                        button_animation.bind_enabled_from(_current_device, "online")
                        ui.functions_buttons.append(button_animation)
                        button_animation.enabled = False


                    
                if (_current_device.led_count == 12):
                    
                    led_positions = [
                        [109.6, 318.8],
                        [202.5, 176.0],
                        [361.9, 99.6],
                        [527.9, 109.6],
                        [667.4, 199.2],
                        [747.1, 348.6],
                        [740.4, 524.6],
                        [647.5, 670.7],
                        [494.7, 750.4],
                        [318.8, 740.4],
                        [176.0, 650.8],
                        [102.9, 491.4],
                    ]
                    
                    
                    
                    def mouse_handler(e: events.MouseEventArguments):
                        #ui.notify(f'{e.type} at ({e.image_x:.1f}, {e.image_y:.1f})')
                        logging.debug(f'In {_current_device.device_id} an image mousclick was detect {e.image_x:.1f}, {e.image_y:.1f}')
                        _click_tolerance = 50
                        if e.type == 'mousedown' and _current_device.online:
                            for i, _position in enumerate(led_positions):
                                if (e.image_x - _position[0])**2 + (e.image_y - _position[1])**2 <= _click_tolerance**2:
                                    with ui.color_picker(
                                        on_pick=lambda e, _led_index = i: (
                                            _current_device.update_lights(_led_index, e.color),
                                            mqtt_controller.send_color(_current_device),
                                            image_color_picker.delete(),
                                        ), 
                                        value=_current_device.lights[i],
                                        
                                    ).props('default-view palette') as image_color_picker:
                                        pass
                                    break
                                    
                            else:
                                ui.notify(f'No LED was clicked', type="negative", color="orange")
                                image_color_picker.delete()
                                
                                
                        
                        
                    
                    with ui.column():
                    
                        with ui.interactive_image(
                            source = led_ring_12_image_path,
                            on_mouse=mouse_handler,
                            events=['mousedown'], 
                        ).classes('w-96 relativ bottom-0 left-4') as image:
                            def update_image_content(lights, device_online):
                                if device_online:
                                    _image_content = ''
                                    for i, color in enumerate(lights):
                                        _image_content += f'''
                                            <circle cx="{led_positions[i][0]}" cy="{led_positions[i][1]}" r="40" fill="{color}" />
                                        ''' 
                                    return _image_content
                                
                            image.bind_content_from(_current_device, "lights", lambda e, i= _current_device.online: update_image_content(e,i))

                with ui.grid(columns=3).style("width: 100%;"):
                    for i in range(_current_device.led_count):
                        button_name = "button" + str(i)
                        with ui.button(icon="lightbulb").style(f"color:{_current_device.lights[i]}!important") as button:
                            button.enabled = False
                            button.name = button_name
                            button.text = "Light " + str(i)
                            ui.color_picker(
                                on_pick=lambda e, led_index=i,: (
                                    _current_device.update_lights(led_index, e.color),
                                    mqtt_controller.send_color(_current_device),
                                )
                            )
                            button.bind_enabled_from(_current_device, "online")
                            ui.led_buttons[_current_device].append(button)
                                
                    
                logging.debug(f"Device {_current_device.device_id} online: {_current_device.online}")

                        


