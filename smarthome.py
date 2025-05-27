from models import *


class SmartHomeSystem:
    def __init__(self):
        self._devices = []

    def add_device(self, device):
        self._devices.append(device)

    def remove_device(self, name):
        self._devices = [d for d in self._devices if d._name != name]

    def turn_all_off(self):
        for device in self._devices:
            device.turn_off()

    def get_total_energy_usage(self):
        return sum(device.get_energy_usage() for device in self._devices)

    def show_devices(self):
        for device in self._devices:
            print(device)