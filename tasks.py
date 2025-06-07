from database import Device, get_device_by_id, save_device
from models import *
from app import app

def control_device(device_id, action, value=None):
    with app.app_context():
        device_row = get_device_by_id(device_id) #Retrieve Device
        device = SmartDevice.from_db(device_row)

        if action == 'on': #Perform Relevant Action
            device.turn_on()
        elif action == 'off':
            device.turn_off()
        elif action == 'set_brightness' and hasattr(device, "brightness"):
            try:
                device.brightness = int(value)
                device.turn_on()
            except ValueError:
                print(f"Invalid brightness value: {value}")
        elif action == 'set_temperature':
            if isinstance(device, (Thermostat, Kettle, Boiler)):
                device.temperature = value
            else:
                print(f"{device_row.name} does not support temperature control.")
        elif action == 'set_colour' and hasattr(device, "colour"):
            try:
                device.colour = Colour[value.upper()]
                device.turn_on()
            except KeyError:
                print(f"Invalid colour: {value}")
        else:
            print(f"Unsupported action or device type: {action}")

        save_device(device_id, device) #Save Changes
