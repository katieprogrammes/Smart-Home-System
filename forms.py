from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional

class AddDeviceForm(FlaskForm):
    name = StringField('Device Name', validators=[DataRequired()])
    type = SelectField('Device Type', choices=[('Light' , 'Light'), ('Thermostat', 'Thermostat'), ('Camera', 'Security Camera'), ('DoorLock', 'Door Lock'), ('Kettle', 'Kettle')])
    temperature = IntegerField('Temperature (if needed)', validators=[Optional()])
    brightness = IntegerField('Set Brightness (if needed)', validators=[Optional()])
    submit = SubmitField('Add Device')

class UpdateTemperatureForm(FlaskForm):
    temperature = IntegerField('New Temperature', validators=[DataRequired()])
    submit = SubmitField('Update Temperature')

class UpdateBrightnessForm(FlaskForm):
    brightness = IntegerField('Set Brightness', validators=[DataRequired()])
    submit = SubmitField('Update Brightness')

class UpdateNameForm(FlaskForm):
    name = StringField('Device Name', validators=[DataRequired()])
    submit = SubmitField('Change Name')