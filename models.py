from abc import ABC, abstractmethod
from enum import Enum

#Colour Options for Lights
class Colour(Enum):
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    PINK = "pink"
    DEFAULT = "default"

#Colour Conversion
def colour_from_string(colour_str):
    try:
        return Colour[colour_str.upper()]
    except (KeyError, AttributeError):
        return Colour.DEFAULT

# Light Base Class
class SuperLight:
    def __init__(self, brightness, colour: Colour):
        self._colour = None
        self.colour = colour
        self._brightness = 0
        self.brightness = brightness 

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, colour):
        if not isinstance(colour, Colour):
            raise TypeError("Colour must be a valid Colour enum")
        if not self._is_colour_allowed(colour):
            raise ValueError(f"This Device cannot change colours")
        self._colour = colour

    def _is_colour_allowed(self, colour: Colour) -> bool:
        return True  # Overridden by subclasses


    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if 0 <= value <= 100:
            self._brightness = value
        else:
            raise ValueError("Brightness must be between 0 and 100")

#Device Base Class
class SmartDevice(ABC):
    total_devices = 0  

    #Initialising
    def __init__(self, name, status=False):
        self._name = name
        self._status = status
        SmartDevice.total_devices += 1

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self.__class__.__name__
    @property
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
    def from_db(cls, device_row): # Factory Method
        device_type = device_row.type
        name = device_row.name
        status = device_row.status
        temp = device_row.temperature
        brightness = device_row.brightness
        colour_str = device_row.colour or "DEFAULT"

        colour_enum = colour_from_string(colour_str)

        if device_type == 'BasicLight':
            return BasicLight(name, brightness or 50, colour_enum, status)
        elif device_type == 'ColourLight':
            return ColourLight(name, brightness or 50, colour_enum, status)
        elif device_type == 'Thermostat':
            return Thermostat(name, temperature=temp, status=status)
        elif device_type == 'Camera':
            return Camera(name, status)
        elif device_type == 'DoorLock':
            return DoorLock(name, status)
        elif device_type == 'Kettle':
            return Kettle(name, set_temp=temp, status=status)
        elif device_type == 'Appliance':
            return Appliance(name, status)
        else:
            raise ValueError(f"Unsupported device type: {device_type}")

    def __str__(self):
        return f"{self._name} ({'On' if self._status else 'Off'})"


#Devices
class BasicLight(SuperLight, SmartDevice):
    ALLOWED_COLOURS = {Colour.DEFAULT}
    
    #Initialising
    def __init__(self, name, brightness, colour: Colour, status=False):
        SmartDevice.__init__(self, name, status)
        SuperLight.__init__(self, brightness, colour)

    def _is_colour_allowed(self, colour: Colour) -> bool:
        return colour in self.ALLOWED_COLOURS
    
    #Overriding Base Class Abstract Method
    def get_energy_usage(self):
        return 5 if self._status else 0

class ColourLight(SuperLight, SmartDevice):
    def __init__(self, name, brightness, colour: Colour, status=False):
        SmartDevice.__init__(self, name, status)
        SuperLight.__init__(self, brightness, colour)

    def _is_colour_allowed(self, colour: Colour) -> bool:
        return True  # All colours allowed
    
    def get_energy_usage(self):
        return 5 if self._status else 0

class Thermostat(SmartDevice):
    def __init__(self, name, temperature=20, status=False):
        super().__init__(name, status)
        self._temperature = temperature

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, temp):
        if 10 <= temp <= 30:
            self._temperature = temp
        else:
            raise ValueError("Temperature must be between 10 and 30")

    def get_energy_usage(self):
        return 50 if self._status else 0


class Camera(SmartDevice):
    def __init__(self, name, status=False):
        super().__init__(name, status)

    def get_energy_usage(self):
        return 10 if self._status else 0


class DoorLock(SmartDevice):
    def __init__(self, name, status=False):
        super().__init__(name, status)

    def get_energy_usage(self):
        return 2 if self._status else 0


class Kettle(SmartDevice):
    def __init__(self, name, set_temp, status=False):
        super().__init__(name, status)
        self._set_temp = set_temp

    @property
    def set_temp(self):
        return self._set_temp

    @set_temp.setter
    def set_temp(self, temp):
        if 50 <= temp <= 100:
            self._set_temp = temp
        else:
            raise ValueError("Temperature must be between 50 and 100")

    def get_energy_usage(self):
        return 20 if self._status else 0

class Appliance(SmartDevice):
    def __init__(self, name, status=False):
        super().__init__(name, status)
        
    def get_energy_usage(self):
        return 10 if self._status else 0
    

#Code for all device behaviour
class SmartHomeSystem:
    def __init__(self):
        self._devices = []

    #Add a device
    def add_device(self, device):
        self._devices.append(device)

    #Remove device
    def remove_device(self, name):
        self._devices = [d for d in self._devices if d._name != name]

    #Turn off all devices
    def turn_all_off(self):
        for device in self._devices:
            device.turn_off()

    #Calculate total energy usage
    def get_total_energy_usage(self):
        return sum(device.get_energy_usage() for device in self._devices)

    def show_devices(self):
        for device in self._devices:
            print(device)