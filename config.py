from distutils.debug import DEBUG
from email.errors import FirstHeaderLineIsContinuationDefect
from decouple import config
from flask import Config

class Config:
    #SECRET_KEY=config('SECRET_KEY')
    SECRET_KEY='password'
    #SQLALCHEMY_DATABASE_URI = 'postgresql://adminDB:3x0w0rks@localhost:5432/DBexoWorks'
    #URI a la BD alojada en Heroku
    SQLALCHEMY_DATABASE_URI = 'postgresql://nmgntihzbdruoo:f6217fe082658c015953604284046c8743268291d990cc2d3c57cae72929278c@ec2-3-211-221-185.compute-1.amazonaws.com:5432/d4i2m2e3fn1svh'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'ubuexoworks@gmail.com'
    MAIL_PASSWORD = '3x0w0rks'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False 
    
class DevelopmentConfig(Config):
    DEBUG=True
   
config = {
     'development': DevelopmentConfig
    }
    