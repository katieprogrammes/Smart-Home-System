from flask import render_template, redirect, url_for, flash
from app import app
from forms import *
from database import *
from models import *
from collections import defaultdict



# Main Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_device():
    form = AddDeviceForm()
    if form.validate_on_submit():
        device = Device(
            name=form.name.data,
            type=form.type.data,
            status=False,
            temperature=form.temperature.data if form.temperature.data else None,
            brightness=form.brightness.data if form.brightness.data else 0
        )
        db.session.add(device)
        db.session.commit()
        return redirect(url_for('view_all'))
    return render_template('add.html', form=form, title='Add Device')

@app.route('/alldevices', methods=['GET'])
def view_all():
    devices = Device.query.all()

    grouped_devices = defaultdict(list)
    device_objects = {}

    for dev in devices:
        grouped_devices[dev.type].append(dev)

        obj = None
        if dev.type == 'BasicLight':
            obj = BasicLight(dev.name, dev.brightness, Colour.DEFAULT, dev.status)
        elif dev.type == 'ColourLight':
            colour_enum = colour_from_string(dev.colour)
            obj = ColourLight(dev.name, dev.brightness, colour_enum, dev.status)
        elif dev.type == 'Kettle':
            obj = Kettle(dev.name, set_temp=dev.temperature or 100, status=dev.status)
        elif dev.type == 'Thermostat':
            obj = Thermostat(dev.name, temperature=dev.temperature or 20, status=dev.status)
        elif dev.type == 'Camera':
            obj = Camera(dev.name, dev.status)
        elif dev.type == 'DoorLock':
            obj = DoorLock(dev.name, dev.status)
     
        if obj is not None and dev.id is not None:
            device_objects[int(dev.id)] = obj

    total_energy = sum(obj.get_energy_usage() for obj in device_objects.values())

    return render_template(
        "devicelist.html",
        grouped_devices=grouped_devices,
        device_objects=device_objects,
        total_energy=total_energy,
        title = 'Devices'
    )

@app.route('/toggle/<int:device_id>', methods=['GET', 'POST']) # To turn device on or off
def toggle_device(device_id):
    device = Device.query.get_or_404(device_id)
    device.toggle_status()
    db.session.commit()
    return redirect('/alldevices')


@app.route("/device/<int:device_id>", methods=['GET', 'POST'])
def device_info(device_id):
    device = Device.query.get_or_404(device_id)  # Fetch Product or Show 404
    return render_template("deviceinfo.html", device=device, title='Device Information')

@app.route('/update_temperature/<int:device_id>', methods=['GET', 'POST'])
def update_temperature(device_id):
    device = Device.query.get_or_404(device_id)

    if device.type not in ['Thermostat', 'Kettle']:
        return "Temperature can't be updated for this device.", 400

    form = UpdateTemperatureForm()

    if form.validate_on_submit():
        new_temp = form.temperature.data
        # Validating input
        if device.type == 'Thermostat' and not (10 <= new_temp <= 30):
            return "Temperature must be between 10 and 30 for a thermostat.", 400
        if device.type == 'Kettle' and not (50 <= new_temp <= 100):
            return "Temperature must be between 50 and 100 for a kettle.", 400

        device.temperature = new_temp
        save_device(device)
        flash("Changes Saved")
        return redirect(url_for('view_all'))
    return render_template('update_temperature.html', form=form, device=device, title='Update Temperature')

@app.route('/update_light/<int:device_id>', methods=['GET', 'POST'])
def update_light(device_id):
    device = Device.query.get_or_404(device_id)

    if device.type not in ('BasicLight', 'ColourLight'):
        return "Brightness can't be updated for this device.", 400

    form = UpdateBrightnessForm()

    if form.validate_on_submit():
        new_brightness = form.brightness.data
        selected_colour = form.colour.data

        # Basic validation
        if not (0 <= new_brightness <= 100):
            return "Brightness must be between 0 and 100.", 400

        # Load the device model from row
        smart_device = SmartDevice.from_db(device)

        # Update brightness
        smart_device.brightness = new_brightness

        # Update colour if applicable
        if hasattr(smart_device, "colour") and selected_colour:
            try:
                smart_device.colour = Colour[selected_colour.upper()]
            except KeyError:
                return "Invalid colour selected.", 400

        save_device(smart_device)
        flash("Changes Saved")
        return redirect(url_for('view_all'))
    return render_template('update_light.html', form=form, device=device, title='Change Light')

@app.route('/update_name/<int:device_id>', methods=['GET', 'POST'])
def update_name(device_id):
    device = Device.query.get_or_404(device_id)

    form = UpdateNameForm()

    if form.validate_on_submit():
        new_name = form.name.data
        device.name = new_name
        db.session.commit()
        return redirect(url_for('view_all'))

    return render_template('update_name.html', form=form, device=device, title='Change Name')

@app.route('/delete/<int:device_id>', methods=['POST'])
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    return redirect(url_for('view_all'))


@app.route('/turn_off_lights', methods=['POST'])
def turn_off_lights():
    lights = Device.query.filter(Device.type.in_(['BasicLight', 'ColouredLight'])).all()
    for light in lights:
        light.status = False
    db.session.commit()
    return redirect(url_for('view_all'))

@app.route('/turn_on_lights', methods=['POST'])
def turn_on_lights():
    lights = Device.query.filter(Device.type.in_(['BasicLight', 'ColouredLight'])).all()
    for light in lights:
        light.status = True
    db.session.commit()
    return redirect(url_for('view_all'))

@app.route('/lock_all_doors', methods=['POST'])
def lock_all_doors():
    locks = Device.query.filter_by(type='DoorLock').all()
    for lock in locks:
        lock.status = True
    db.session.commit()
    return redirect(url_for('view_all'))

@app.route('/maximum_security',  methods=['GET','POST'])
def max_security():
    locks = Device.query.filter_by(type='DoorLock').all()
    for lock in locks:
        lock.status = True
    db.session.commit()
    cameras = Device.query.filter_by(type='Camera').all()
    for camera in cameras:
        camera.status = True
    db.session.commit()
    flash("Maximum Security On")
    return redirect(url_for('home'))
