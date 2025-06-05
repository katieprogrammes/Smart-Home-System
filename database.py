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

def save_device(device):
    db_device = Device.query.filter_by(name=device.name).first()
    if db_device:
        db_device.status = device.is_on
        if hasattr(device, "get_temperature"):
            db_device.temperature = device.temperature
        if hasattr(device, "brightness"):
            db_device.brightness = device.brightness
        if hasattr(device, "colour"):
            db_device.colour = device.colour.name      
    else:
        # Create new device
        db_device = Device(
            name=device.name,
            type=device.type, 
            status=device.is_on,
            temperature=getattr(device, "temperature", None),
            brightness=getattr(device, "brightness", None),
            colour=getattr(device.colour, "name", None) if hasattr(device, "colour") else None
        )
        db.session.add(db_device)
    db.session.commit()


