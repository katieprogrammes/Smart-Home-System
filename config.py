import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'devices.db')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SCHEDULER_API_ENABLED = True
    
