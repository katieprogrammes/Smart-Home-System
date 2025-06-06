from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.Boolean, default=False)
    temperature = db.Column(db.Integer, nullable=True)
    brightness = db.Column(db.Integer, nullable=True)
    colour = db.Column(db.String(20), nullable=True)

    def toggle_status(self): # To turn on and off
        self.status = not self.status

def get_all_devices():
        return Device.query.all()    

def get_device_by_id(device_id):
    return Device.query.get(device_id)

def save_device(device_id, device):
    db_device = Device.query.get(device_id)
    if not db_device:
        raise ValueError(f"No device found in DB with ID {device_id}")

    db_device.status = device.is_on
    if hasattr(device, "temperature"):
        db_device.temperature = device.temperature
    if hasattr(device, "brightness"):
        db_device.brightness = device.brightness
    if hasattr(device, "colour") and device.colour:
        db_device.colour = device.colour.name

    db.session.commit()

