from flask import render_template, redirect, url_for, flash, request
from app import app, scheduler
from forms import *
from database import *
from models import *
from tasks import *
from collections import defaultdict
from datetime import datetime



#Main Routes
@app.route('/')
def home():
    return render_template('index.html')

#Add a Device
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
        flash("Device Added")
        return redirect(url_for('view_all'))
    return render_template('add.html', form=form, title='Add Device')

#Device Dashboard
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

@app.route('/toggle/<int:device_id>', methods=['GET', 'POST']) #To Turn Device On or Off
def toggle_device(device_id):
    device = Device.query.get_or_404(device_id)
    device.toggle_status()
    db.session.commit()
    return redirect('/alldevices')

#Device Information Page
@app.route("/device/<int:device_id>", methods=['GET', 'POST'])
def device_info(device_id):
    device = Device.query.get_or_404(device_id)  #Fetch Device or Show 404
    return render_template("deviceinfo.html", device=device, title='Device Information')

#Updating Temperature
@app.route('/update_temperature/<int:device_id>', methods=['GET', 'POST'])
def update_temperature(device_id):
    device = Device.query.get_or_404(device_id)

    if device.type not in ['Thermostat', 'Kettle', 'Boiler']:
        raise InvalidDeviceTypeError("Temperature can't be updated for this device.")

    form = UpdateTemperatureForm()

    if form.validate_on_submit():
        new_temp = form.temperature.data
        #Validating input
        if device.type == 'Thermostat' and not (10 <= new_temp <= 30):
            flash("Temperature must be between 10 and 30 for a Thermostat.", "error")
            return redirect(url_for('update_temperature', device_id=device.id))
        if device.type == 'Kettle' and not (50 <= new_temp <= 100):
            flash("Temperature must be between 50 and 100 for a Kettle.", "error")
            return redirect(url_for('update_temperature', device_id=device.id))
        if device.type == 'Boiler' and not (40 <= new_temp <= 60):
            flash("Temperature must be between 40 and 60 for a Kettle.", "error")
            return redirect(url_for('update_temperature', device_id=device.id))

        device.temperature = new_temp
        db.session.commit()
        flash("Changes Saved")
        return redirect(url_for('view_all'))
    return render_template('update_temperature.html', form=form, device=device, title='Update Temperature')

#Updating Light Settings
@app.route('/update_light/<int:device_id>', methods=['GET', 'POST'])
def update_light(device_id):
    device = Device.query.get_or_404(device_id)

    if device.type not in ('BasicLight', 'ColourLight'):
        raise InvalidDeviceTypeError("Brightness can't be updated for this device.")

    form = UpdateBrightnessForm()

    if form.validate_on_submit():
        new_brightness = form.brightness.data
        selected_colour = form.colour.data

        # Basic validation
        if not (0 <= new_brightness <= 100):
            flash("Brightness must be between 0 and 100.", "error")
            return redirect(url_for('update_light', device_id=device.id))


        # Update brightness
        device.brightness = new_brightness

        # Update colour if applicable
        if hasattr(device, "colour") and selected_colour:
            try:
                device.colour = Colour[selected_colour.upper()].value  
            except KeyError:
                raise InvalidDeviceTypeError("Invalid colour selected.")

        db.session.commit()
        flash("Changes Saved")
        return redirect(url_for('view_all'))
    return render_template('update_light.html', form=form, device=device, title='Change Light')

#Updating Device Name
@app.route('/update_name/<int:device_id>', methods=['GET', 'POST'])
def update_name(device_id):
    device = Device.query.get_or_404(device_id)

    form = UpdateNameForm()

    if form.validate_on_submit():
        new_name = form.name.data
        device.name = new_name
        db.session.commit()
        flash('Changes Saved')
        return redirect(url_for('view_all'))

    return render_template('update_name.html', form=form, device=device, title='Change Name')

#Delete a Device
@app.route('/delete/<int:device_id>', methods=['POST'])
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    flash('Device Deleted')
    return redirect(url_for('view_all'))


@app.route('/turn_off_lights', methods=['POST']) #Turn all Lights Off
def turn_off_lights():
    lights = Device.query.filter(Device.type.in_(['BasicLight', 'ColourLight'])).all()
    for light in lights:
        light.status = False
    db.session.commit()
    flash('All Lights Off')
    return redirect(url_for('view_all'))

@app.route('/turn_on_lights', methods=['POST']) #Turn all Lights On
def turn_on_lights():
    lights = Device.query.filter(Device.type.in_(['BasicLight', 'ColourLight'])).all()
    for light in lights:
        light.status = True
    db.session.commit()
    flash('All Lights On')
    return redirect(url_for('view_all'))

@app.route('/lock_all_doors', methods=['POST']) #Lock all Doors
def lock_all_doors():
    locks = Device.query.filter_by(type='DoorLock').all()
    for lock in locks:
        lock.status = True
    db.session.commit()
    flash('Doors Locked')
    return redirect(url_for('view_all'))

@app.route('/maximum_security',  methods=['GET','POST']) #Maximum Security Toggle
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
            value = None

        #Compose Job ID
        job_id_parts = [device_id, action]
        if value is not None:
            job_id_parts.append(str(value))
        job_id_parts.append(schedule_time.strftime('%Y%m%d%H%M%S'))
        job_id = "|".join(job_id_parts)

        args = [device_id, action]
        if value is not None:
            if action == "set_colour":
                args.append(value.upper())
            else:
                args.append(value)

        #Schedule the Job
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
    scheduler.remove_job(job_id)
    print("Jobs after delete:", [job.id for job in scheduler.get_jobs()])
    flash('Job deleted successfully.')
    return redirect(url_for('viewtasks'))

@app.route('/edit_job/<job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    form = ScheduleForm()

    #Split Job ID Format
    parts = job_id.split('|')
    if len(parts) not in [3, 4]:
        flash('Invalid job format.')
        return redirect(url_for('viewtasks'))

    if len(parts) == 4:
        device_id, action, value, time_str = parts
    else:
        device_id, action, time_str = parts
        value = None

    schedule_time = datetime.strptime(time_str, '%Y%m%d%H%M%S')

    #Populate Form with Existing Job Choices
    devices = get_all_devices()
    form.device_id.choices = [(str(d.id), d.name) for d in devices]

    if request.method == 'GET':
        form.device_id.data = device_id
        form.action.data = action
        form.schedule_time.data = schedule_time
        if value:
            if action == "set_colour":
                form.colour.data = value
            else:
                form.value.data = value

    if form.validate_on_submit():
        #Remove Old Job
        scheduler.remove_job(job_id)

        #Get Values from Form
        device_id = form.device_id.data
        action = form.action.data
        schedule_time = form.schedule_time.data

        if action == "set_colour":
            value = form.colour.data
        elif action in ["set_brightness", "set_temperature"]:
            value = form.value.data
        else:
            value = None

        #Build New Job ID
        new_parts = [device_id, action]
        if value is not None:
            new_parts.append(str(value))
        new_parts.append(schedule_time.strftime('%Y%m%d%H%M%S'))
        new_job_id = "|".join(new_parts)

        #Build New args
        args = [device_id, action]
        if value is not None:
            args.append(value.upper() if action == "set_colour" else value)

        #Add New Job
        scheduler.add_job(
            id=new_job_id,
            func=control_device,
            args=args,
            trigger='date',
            run_date=schedule_time,
            next_run_time=schedule_time,
            replace_existing=True
        )

        flash('Job updated successfully.')
        return redirect(url_for('viewtasks'))

    return render_template('schedule.html', form=form, editing=True)

#Error Handling
@app.errorhandler(InvalidDeviceTypeError)
def handle_invalid_device_type(error):
    return render_template('error.html', message=error.message), 400
