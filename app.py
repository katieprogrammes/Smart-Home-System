from flask import Flask
from database import db, Device
from config import Config
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

migrate = Migrate(app, db)
db.init_app(app)

# Run the app and create database
if __name__ == '__main__':
    with app.app_context():  # Needed for DB operations
        db.create_all()      # Creates the database and tables
    app.run(debug=True)



from routes import *








