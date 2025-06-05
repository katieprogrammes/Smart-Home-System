from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional
from models import Colour

class AddDeviceForm(FlaskForm):
    name = StringField('Device Name', validators=[DataRequired()])
    type = SelectField('Device Type', choices=[('BasicLight' , 'Light'), ('ColourLight', 'Multi-Coloured Light'), ('Thermostat', 'Thermostat'), ('Camera', 'Security Camera'), ('DoorLock', 'Door Lock'), ('Kettle', 'Kettle'), ('Appliance', 'Appliance')])
    temperature = IntegerField('Temperature (if needed)', validators=[Optional()])
    brightness = IntegerField('Set Brightness (if needed)', validators=[Optional()])
    submit = SubmitField('Add Device')

class UpdateTemperatureForm(FlaskForm):
    temperature = IntegerField('New Temperature', validators=[DataRequired()])
    submit = SubmitField('Update Temperature')

class UpdateBrightnessForm(FlaskForm):
    brightness = IntegerField('Set Brightness', validators=[DataRequired()])
    colour = SelectField('Set Colour (optional)', choices=[(c.name, c.value.title()) for c in Colour], validators=[Optional()])
    submit = SubmitField('Save Changes')

class UpdateNameForm(FlaskForm):
    name = StringField('Device Name', validators=[DataRequired()])
    submit = SubmitField('Change Name')