from flask import render_template, redirect, url_for, flash, request
from app import app, scheduler
from forms import *
from database import *
from models import *
from tasks import *
from collections import defaultdict
from datetime import datetime



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
            obj = Kettle(dev.name, temperature=dev.temperature or 100, status=dev.status)
        elif dev.type == 'Boiler':
            obj = Boiler(dev.name, temperature=dev.temperature or 50, status=dev.status)
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

    if device.type not in ['Thermostat', 'Kettle', 'Boiler']:
        return "Temperature can't be updated for this device.", 400

    form = UpdateTemperatureForm()

    if form.validate_on_submit():
        new_temp = form.temperature.data
        # Validating input
        if device.type == 'Thermostat' and not (10 <= new_temp <= 30):
            return "Temperature must be between 10 and 30 for a thermostat.", 400
        if device.type == 'Kettle' and not (50 <= new_temp <= 100):
            return "Temperature must be between 50 and 100 for a kettle.", 400
        if device.type == 'Boiler' and not (40 <= new_temp <= 60):
            return "Temperature must be between 40 and 60 for a kettle.", 400

        device.temperature = new_temp
        db.session.commit()
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

        # Update brightness
        device.brightness = new_brightness

        # Update colour if applicable
        if hasattr(device, "colour") and selected_colour:
            try:
                device.colour = Colour[selected_colour.upper()]
            except KeyError:
                return "Invalid colour selected.", 400

        db.session.commit()
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

#Scheduling Pages
@app.route('/viewschedules', methods=['GET', 'POST'])
def viewtasks():
    jobs = scheduler.get_jobs()
    devices = get_all_devices()
    device_lookup = {str(d.id): d.name for d in devices}
    return render_template('scheduled_tasks.html', jobs=jobs, device_lookup=device_lookup)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    form = ScheduleForm()
    devices = get_all_devices()
    form.device_id.choices = [(str(d.id), d.name) for d in devices]

    if form.validate_on_submit():
        device_id = form.device_id.data
        action = form.action.data
        schedule_time = form.schedule_time.data

        if action == "set_colour":
            value = form.colour.data
        elif action == "set_brightness" or action == "set_temperature":
            value = form.value.data 
        else:
            value = 0

        # Compose job ID
        job_id_parts = [device_id, action]
        if value is not None:
            job_id_parts.append(str(value))
        job_id_parts.append(schedule_time.strftime('%Y%m%d%H%M%S'))
        job_id = "_".join(job_id_parts)

        args = [device_id, action]
        if value is not None:
            if action == "set_colour":
                args.append(value.upper())
            else:
                args.append(value)

        # Schedule the job
        scheduler.add_job(
            id=job_id,
            func=control_device,
            args=args,
            trigger='date',
            run_date=schedule_time,
            next_run_time=schedule_time,
            replace_existing=True
        )

        flash('Task scheduled!')
        return redirect(url_for('viewtasks'))
    return render_template('schedule.html', form=form)

@app.route('/delete_job/<job_id>')
def delete_job(job_id):
    print("Jobs before delete:", [job.id for job in scheduler.get_jobs()])
    scheduler.remove_job(job_id)  # without jobstore param
    print("Jobs after delete:", [job.id for job in scheduler.get_jobs()])
    flash('Job deleted successfully.')
    return redirect(url_for('viewtasks'))

@app.route('/edit_job/<job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    form = ScheduleForm()

    # Split Job ID Format
    parts = job_id.split('_')
    if len(parts) not in [3, 4]:
        flash('Invalid job format.')
        return redirect(url_for('viewtasks'))

    # Parse Parts
    if len(parts) == 4:
        device_id, action, value, time_str = parts
    else:
        device_id, action, time_str = parts
        value = None

    schedule_time = datetime.strptime(time_str, '%Y%m%d%H%M%S')

    #Populate Device Choices
    devices = get_all_devices()
    form.device_id.choices = [(str(d.id), d.name) for d in devices]

    if request.method == 'GET':
        form.device_id.data = device_id
        form.action.data = action
        form.schedule_time.data = schedule_time
        if value is not None:
            form.value.data = value

    if form.validate_on_submit():
        # Remove old job
        scheduler.remove_job(job_id)

        # Build new job ID
        new_parts = [form.device_id.data, form.action.data]
        if form.value.data is not None:
            new_parts.append(str(form.value.data))
        new_parts.append(form.schedule_time.data.strftime('%Y%m%d%H%M%S'))
        new_job_id = "_".join(new_parts)

        # Build new args
        new_args = [form.device_id.data, form.action.data]
        if form.value.data is not None:
            new_args.append(form.value.data)

        # Add new job
        scheduler.add_job(
            id=new_job_id,
            func=control_device,
            args=new_args,
            trigger='date',
            run_date=form.schedule_time.data,
            replace_existing=True
        )

        flash('Job updated successfully.')
        return redirect(url_for('viewtasks'))

    return render_template('schedule.html', form=form, editing=True)
