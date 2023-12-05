import paho.mqtt.client as mqtt
from nicegui import ui
import json

# Define MQTT broker settings
broker_address = "172.17.0.1"
broker_port = 1883
broker_username = "ui"
broker_password = "password"


# Define MQTT topics
topics = ["test/leds/command/" + str(i) for i in range(12)]
topic_state = "test/leds/state"

# Create MQTT client instance
client = mqtt.Client()


def parse_json_message(json_message):
    led_colors = {}
    try:
        data = json.loads(json_message)
        for led_index, color_data in data.items():
            red = color_data.get("red", 0)
            green = color_data.get("green", 0)
            blue = color_data.get("blue", 0)
            color_hex = "#{:02x}{:02x}{:02x}".format(red, green, blue)
            led_colors[int(led_index)] = color_hex
    except json.JSONDecodeError:
        print("Invalid JSON message")
        
    return led_colors


def set_led_button_color(led_colors):
    for i, e in enumerate(led_colors.values()):
        ui.led_buttons[i].style(f"color:{led_colors[i]}!important"),


def send_color(led_index, color):
    # Parse color into separate RGB values
    red, green, blue = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

    # Create JSON payload
    payload = {"red": red, "green": green, "blue": blue}

    # Publish payload to MQTT topic
    topic = topics[led_index]
    client.publish(topic, json.dumps(payload))


# Define MQTT event handlers
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    # Subscribe to topics upon successful connection
    client.subscribe(topic_state)
    # Update UI with connection status
    ui.status_label.text = "Connected to MQTT broker " + broker_address
    ui.connect_button.text = "Disconnect"  # Change connect button text to "Disconnect"
    ui.broker_address_textbox.enabled = False
    ui.broker_port_textbox.enabled = False
    ui.connect_button.props("color=negative")

    for i in range(len(ui.led_buttons)):
        ui.led_buttons[i].enabled = True


def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " " + str(msg.payload))
    print(parse_json_message(msg.payload))


def on_publish(client, userdata, mid):
    print("Message published")


def on_disconnect(client, userdata, rc):
    ui.connect_button.text = "Connect"
    ui.status_label.text = "Disconnected from MQTT broker"
    print("Disconnected from MQTT broker")
    ui.broker_port_textbox.enabled = True
    ui.broker_address_textbox.enabled = True
    ui.connect_button.props("color=positive")
    ui.notify("Disconnected from MQTT broker", type="negative")
    for i in range(len(ui.led_buttons)):
        ui.led_buttons[i].enabled = False


# Set MQTT event handlers
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_disconnect = on_disconnect

# Set MQTT broker credentials (if required)
client.username_pw_set(broker_username, broker_password)


# Connect to MQTT broker
def connect_to_mqtt():
    ui.connect_button.props("loading=true")
    ui.status_label.text = "Connecting to MQTT broker..."

    try:
        # Start MQTT network loop
        client.connect(broker_address, broker_port)
        client.loop_start()
    except ConnectionRefusedError:
        print("MQTT connection refused")
        # Update UI with connection status
        ui.status_label.text = "MQTT connection refused"
    except TimeoutError:
        print("MQTT connection timed out")
        # Update UI with connection status
        ui.status_label.text = "MQTT connection timed out"
    except Exception as e:
        print("MQTT connection error:", str(e))
        # Update UI with connection status
        ui.status_label.text = "MQTT connection error: " + str(e)
    else:
        ui.notify("Connected to MQTT broker " + broker_address, type="positive")


def disconnect_from_mqtt():
    ui.status_label.text = "Disonnecting from MQTT broker..."
    # Stop MQTT network loop
    client.loop_stop()
    client.disconnect()


ui.label("LED Controller UI").style(
    "color: #ffff ; font-size: 400%; font-weight: 700; bold: true;"
)
ui.label("provided by David Sokolowski").style(
    "color: #ffff ; font-size: 100%; font-weight: 0; bold: false;position: relative;bottom: 30px;right: 0px;"
)

with ui.card():
    ui.status_label = ui.label(text="Connecting to MQTT broker...")
    # Create UI element for connecting to MQTT broker
    ui.connect_button = ui.button(
        text="Connect",
        on_click=lambda: connect_to_mqtt()
        if not client.is_connected()
        else disconnect_from_mqtt(),
    )
    # Create UI element for displaying connection status

    with ui.row():
        # Create UI element for changing broker address
        ui.broker_address_textbox = ui.input(
            label="MQTT Broker Address",
            value=broker_address,
            placeholder="IP format: 172.17.0.1",
            autocomplete=["172.17.0.1", "192.168.1.10"],
            on_change=lambda: set_ip_value(),
        )
        # Create UI element for changing broker address
        ui.broker_port_textbox = ui.number(
            label="MQTT Broker Port",
            value=broker_port,
            placeholder="default: 1883",
            format="%.0f",
            on_change=lambda: set_port_value(),
        )


def set_ip_value():
    global broker_address  # Add this line to access the global variable
    broker_address = ui.broker_address_textbox.value


def set_port_value():
    global broker_port  # Add this line to access the global variable
    broker_port = int(ui.broker_port_textbox.value)


connect_to_mqtt()


# ui.separator()


# Create UI elements for controlling LEDs
with ui.tabs() as tabs:
    tab_1 = ui.tab("Controller 1", icon="online_prediction")
    tab_2 = ui.tab("Controller 2", icon="online_prediction")
    tab_3 = ui.tab("Controller 3", icon="online_prediction")

with ui.tab_panels(tabs, value=tab_1) as panels:
    with ui.tab_panel(tab_1):
        # Create UI elements for controlling LEDs
        ui.led_buttons = []
        with ui.grid(columns=3):
            for i in range(12):
                button_name = "button" + str(i)
                with ui.button(icon="lightbulb") as button:
                    button.enabled = False
                    # button.props("round")
                    button.name = button_name
                    button.text = "LED " + str(i)
                    color = ui.color_picker(
                        on_pick=lambda e, led_index=i, button=button: (
                            button.style(f"color:{e.color}!important"),
                            send_color(led_index, e.color),
                        )
                    )
                    ui.led_buttons.append(button)


# Run the program in window mode
ui.run(
    dark=None,
    title="MQTT LED Controller",
    reload=True,
    native=False,
    favicon="💡",
)
