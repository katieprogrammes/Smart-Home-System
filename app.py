from flask import Flask
from database import db, Device
from config import Config
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

migrate = Migrate(app, db)
db.init_app(app)

# Run the app and create database
if __name__ == '__main__':
    with app.app_context():  # Needed for DB operations
        db.create_all()      # Creates the database and tables
    app.run(debug=True)

# Scheduling devices
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

def toggle_device_job(device_id):
    with app.app_context():
        device = Device.query.get(device_id)
        if device:
            device.status = not device.status
            db.session.commit()
            print(f"Toggled device {device.name} at {datetime.now()}")

@app.route('/schedule/<int:id>', methods=['GET', 'POST'])
def schedule_device(id):
    if request.method == 'POST':
        time_str = request.form['time'] 
        run_time = datetime.strptime(time_str, "%d-%m-%Y %H:%M:%S")
        job_id = f"toggle-{id}-{run_time}"

        scheduler.add_job(
            id=job_id,
            func=toggle_device_job,
            args=[id],
            trigger='date',
            run_date=run_time
        )
        return redirect('/')
    
    return render_template('schedule.html', device_id=id)

from routes import *









