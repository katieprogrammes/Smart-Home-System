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

#Light Base Class
class SuperLight:
    def __init__(self, brightness, colour: Colour):
        self._colour = None
        self.colour = colour
        self._brightness = 0
        self.brightness = brightness 

    @property
    def colour(self):
        return self._colour

    #Colour Validation
    @colour.setter
    def colour(self, colour):
        if not isinstance(colour, Colour):
            raise TypeError("Colour must be a valid Colour enum")
        if not self._is_colour_allowed(colour):
            raise ValueError(f"This Device cannot change colours")
        self._colour = colour

    def _is_colour_allowed(self, colour: Colour) -> bool:
        return True  #Overridden by Subclasses


    @property
    def brightness(self):
        return self._brightness

    #Brightness Validation
    @brightness.setter
    def brightness(self, value):
        if 0 <= value <= 100:
            self._brightness = value
        else:
            raise ValueError("Brightness must be between 0 and 100")

#Temperature Base Class
class SuperTemp:
    def __init__(self, temperature):
        self._temperature = 0
        self.temperature = temperature 

    @property
    def temperature(self):
        return self._temperature
    
    #Temperature Validation
    @temperature.setter
    def temperature(self, value):
        if 0 <= value <= 100:
            self._temperature = value
        else:
            raise ValueError("Temperature must be between 0 and 100")

#Device Base Class
class SmartDevice(ABC):
    total_devices = 0  

    #Initialising
    def __init__(self, name, status=False):
        self._name = name
        self._status = status
        SmartDevice.total_devices += 1

    #Getter Methods
    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self.__class__.__name__
    
    @property
    def is_on(self):
        return self._status

    #Shared Methods
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
            return Kettle(name, temperature=temp, status=status)
        elif device_type == 'Boiler':
            return Boiler(name, temperature=temp, status=status)
        elif device_type == 'Appliance':
            return Appliance(name, status)
        else:
            raise ValueError(f"Unsupported device type: {device_type}")

    def __str__(self):
        return f"{self._name} ({'On' if self._status else 'Off'})"


#Device Subclasses
class BasicLight(SuperLight, SmartDevice):
    ALLOWED_COLOURS = {Colour.DEFAULT} #Restrcits Colour Options
    
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
        return True  #All Colours Allowed
    
    def get_energy_usage(self):
        return 5 if self._status else 0

class Kettle(SuperTemp, SmartDevice):
    def __init__(self, name, temperature, status=False):
        SmartDevice.__init__(self, name, status)
        SuperTemp.__init__(self, temperature)

    #Overwriting Base Class Temperature Validation
    @SuperTemp.temperature.setter
    def temperature(self, value):
        if 60 <= value <= 100:
            self._temperature = value
        else:
            raise ValueError("Temperature must be between 60 and 100")    

    def get_energy_usage(self):
        return 20 if self._status else 0
    
class Thermostat(SuperTemp, SmartDevice):
    def __init__(self, name, temperature, status=False):
        SmartDevice.__init__(self, name, status)
        SuperTemp.__init__(self, temperature)

    @SuperTemp.temperature.setter
    def temperature(self, value):
        if 10 <= value <= 30:
            self._temperature = value
        else:
            raise ValueError("Temperature must be between 10 and 30")   
         
    def get_energy_usage(self):
        return 50 if self._status else 0

class Boiler(SuperTemp, SmartDevice):
    def __init__(self, name, temperature, status=False):
        SmartDevice.__init__(self, name, status)
        SuperTemp.__init__(self, temperature)

    @SuperTemp.temperature.setter
    def temperature(self, value):
        if 40 <= value <= 60:
            self._temperature = value
        else:
            raise ValueError("Temperature must be between 40 and 60")    

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

class Appliance(SmartDevice):
    def __init__(self, name, status=False):
        super().__init__(name, status)
        
    def get_energy_usage(self):
        return 10 if self._status else 0
    

#Code for All Device Behaviour
class SmartHomeSystem:
    def __init__(self):
        self._devices = []

    #Add a Device
    def add_device(self, device):
        self._devices.append(device)

    #Remove a Device
    def remove_device(self, name):
        self._devices = [d for d in self._devices if d._name != name]

    #Turn Off All Devices
    def turn_all_off(self):
        for device in self._devices:
            device.turn_off()

    #Calculate Total Energy Usage
    def get_total_energy_usage(self):
        return sum(device.get_energy_usage() for device in self._devices)

    #Show Device Status
    def show_devices(self):
        for device in self._devices:
            print(device)

#Error Handling
class InvalidDeviceTypeError(Exception):
    def __init__(self, message):
        self.message = message