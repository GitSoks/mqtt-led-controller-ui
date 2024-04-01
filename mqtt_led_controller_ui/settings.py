# the address of the MQTT broker (e.g. "mqtt_broker" for Docker, "localhost" for local)
BROKER_ADRESS: str = "mqtt_broker"

BROKER_PORT: int = 1883  # the port of the MQTT broker (default: 1883)
BROKER_USERNAME: str = "ui"  # the username for the MQTT broker
BROKER_PASSWORD: str = "password"  # the password for the MQTT broker

ADD_DUMMY_TEST_DEVICES: bool = (
    True  # if True, the UI will add test devices to the list of devices
)
ENABLE_PERFORMANCE_TEST_BUTTON: bool = (
    True  # if True, the UI will add a button to test the performance of the devices
)

led_ring_12_image_path: str = (
    "./media/led_ring.png"  # the path to the image of the 12-LED ring
)
