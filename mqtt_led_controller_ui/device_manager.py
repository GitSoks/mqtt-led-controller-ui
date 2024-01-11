import logging


class Device:
    def __init__(self, device_id: str):
        self.device_id = device_id
        self._online = False
        self._online_str = ""
        self._led_count = 1
        self.lights = [str(i) for i in range(self._led_count)]
        self._online_change_event = None
        self.retain = True

    @property
    def led_count(self):
        return self._led_count

    @led_count.setter
    def led_count(self, count: int):
        if self._led_count != count:
            self._led_count = count
            self.lights = [str(i) for i in range(count)]

    @property
    def online(self):
        return self._online
    
    @property
    def online_str(self):
        if (self._online):
            return "online"
        else:
            return "offline"
    

    @online.setter
    def online(self, status: bool):
        if self._online != status:
            self._online = status
            if self._online_change_event is not None:
                self._online_change_event(status)

    def update_lights(self, index: int, color: str):
        try:
            self.lights[index] = color
        except IndexError:
            logging.info("Index out of range")


    def set_online_change_event(self, event):
        self._online_change_event = event


class DeviceManager:
    def __init__(self):
        self.devices = []
        self.selected_device = None

    def add_device(self, device: Device):
        self.devices.append(device)
        self.selected_device = device.device_id

    def list_devices(self):
        for device in self.devices:
            logging.info(
                f"Device ID: {device.device_id}, Online: {device.online}, Lights: {device.lights}"
            )

    def get_online_devices(self):
        return [device for device in self.devices if device.online]
