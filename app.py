from flask import Flask
from database import db, Device
from config import Config
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
app.config.from_object(Config)

migrate = Migrate(app, db)
db.init_app(app)

#Scheduling
scheduler = BackgroundScheduler()
scheduler.start()

# Run the app and create database
if __name__ == '__main__':
    with app.app_context():  
        db.create_all()      
    app.run(debug=True)

from routes import *











