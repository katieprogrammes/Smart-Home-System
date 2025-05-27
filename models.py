from abc import ABC, abstractmethod

class SmartDevice(ABC):
    total_devices = 0  # Class variable

    def __init__(self, name, status=False):
        self._name = name
        self._status = status
        SmartDevice.total_devices += 1

    def get_name(self):
        return self._name

    def is_on(self):
        return self._status

    def turn_on(self):
        self._status = True

    def turn_off(self):
        self._status = False

    @abstractmethod
    def get_energy_usage(self):
        pass

    @classmethod
    def from_db(cls, device_row): # Getting correct device subtype
        device_type = device_row.type
        name = device_row.name
        status = device_row.status
        temp = device_row.temperature
        brightness = device_row.brightness

        if device_type == 'Light':
            return Light(name, status, brightness=brightness)
        elif device_type == 'Thermostat':
            return Thermostat(name, temperature=temp, status=status)
        elif device_type == 'Camera':
            return Camera(name, status)
        elif device_type == 'DoorLock':
            return DoorLock(name, status)
        elif device_type == 'Kettle':
            return Kettle(name, setTemp=temp, status=status)
        else:
            raise ValueError(f"Unsupported device type: {device_type}")

    def __str__(self):
        return f"{self._name} ({'On' if self._status else 'Off'})"


class Light(SmartDevice):
    def __init__(self, name, brightness, status=False):
        super().__init__(name, status)
        self._brightness = brightness

    def set_brightness(self, brightness):
        if 0 <= brightness <= 1000:
            self._brightness = brightness
        else:
            raise ValueError("Temperature must be between 0 and 100")

    def get_brightness(self):
        return self._brightness

    def get_energy_usage(self):
        return 5 if self._status else 0


class Thermostat(SmartDevice):
    def __init__(self, name, temperature=20, status=False):
        super().__init__(name, status)
        self._temperature = temperature

    def set_temperature(self, temp):
        if 10 <= temp <= 30:
            self._temperature = temp
        else:
            raise ValueError("Temperature must be between 10 and 30")

    def get_temperature(self):
        return self._temperature

    def get_energy_usage(self):
        return 50 if self._status else 0


class Camera(SmartDevice):
    def get_energy_usage(self):
        return 10 if self._status else 0


class DoorLock(SmartDevice):
    def get_energy_usage(self):
        return 2 if self._status else 0


class Kettle(SmartDevice):
    def __init__(self, name, setTemp, status=False):
        super().__init__(name, status)
        self._setTemp = setTemp

    def set_temp(self, temp):
        if 50 <= temp <= 100:
            self._setTemp = temp
        else:
            raise ValueError("Temperature must be between 50 and 100")

    def get_energy_usage(self):
        return 20 if self._status else 0
