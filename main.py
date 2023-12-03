import paho.mqtt.client as mqtt
from nicegui import ui
import json

# Define MQTT broker settings
broker_address = "192.168.1.10"
broker_port = 1883
broker_username = "ui"
broker_password = "password"

# Define MQTT topics
topics = ["test/leds/command/" + str(i) for i in range(12)]

# Create MQTT client instance
client = mqtt.Client()


# Define MQTT event handlers
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    # Subscribe to topics upon successful connection
    for topic in topics:
        client.subscribe(topic)


def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " " + str(msg.payload))


def on_publish(client, userdata, mid):
    print("Message published")


def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT broker")


# Set MQTT event handlers
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_disconnect = on_disconnect

# Set MQTT broker credentials (if required)
client.username_pw_set(broker_username, broker_password)

# Connect to MQTT broker
client.connect(broker_address, broker_port)

# Start MQTT network loop
client.loop_start()


def send_color(led_index, color):
    # Parse color into separate RGB values
    red, green, blue = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

    # Create JSON payload
    payload = {"red": red, "green": green, "blue": blue}

    # Publish payload to MQTT topic
    topic = topics[led_index]
    client.publish(topic, json.dumps(payload))


# Create UI elements for controlling LEDs
led_buttons = []
with ui.grid(rows=6, columns=6):
    for i in range(12):
        button_name = "button" + str(i)
        with ui.button(icon="colorize") as button:
            button.name = button_name
            color = ui.color_picker(
                on_pick=lambda e, led_index=i, button=button: (
                    button.style(f"background-color:{e.color}!important"),
                    send_color(led_index, e.color),
                )
            )
            led_buttons.append(button_name)
        ui.label(text=str(i))

# Run the program in window mode
ui.run(dark=None, title="MQTT LED Controller", reload=True, native=True)

# Disconnect from MQTT broker
# client.loop_stop()
# client.disconnect()
