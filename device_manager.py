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
