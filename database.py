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

    def toggle_status(self): # To turn on and off
        self.status = not self.status