import paho.mqtt.client as mqtt

# Define MQTT broker settings
broker_address = "192.168.1.10"
broker_port = 1883
broker_username = "ui"
broker_password = "password"

# Define MQTT topics
topic1 = "leds"
topic2 = "test/leds/#"


# Define MQTT event handlers
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    # Subscribe to topics upon successful connection
    client.subscribe(topic1)
    client.subscribe(topic2)


def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " " + str(msg.payload))


def on_publish(client, userdata, mid):
    print("Message published")


def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT broker")


# Create MQTT client instance
client = mqtt.Client()

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

# Publish messages
client.publish(topic1, "Hello, topic1!")

with ui.button(icon="colorize") as button:
    ui.color_picker(
        on_pick=lambda e: button.style(f"background-color:{e.color}!important")
    )


ui.run()
# Keep the program running
# while True:
#    pass


# Disconnect from MQTT broker
# client.loop_stop()
# client.disconnect()
