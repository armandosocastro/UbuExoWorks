from distutils.debug import DEBUG
from email.errors import FirstHeaderLineIsContinuationDefect
from decouple import config
from flask import Config

class Config:
    #SECRET_KEY=config('SECRET_KEY')
    SECRET_KEY='password'
    #URI a la BD alojada en Heroku
    SQLALCHEMY_DATABASE_URI = 'postgresql://iqouknmpzctbyh:1cefbbf5a3b2d75005e7507d9b587668fe85f30142e5daf2fc097502ce348c58@ec2-52-206-182-219.compute-1.amazonaws.com:5432/d26onqthf08v3t'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'ubuexoworks@gmail.com'
    MAIL_PASSWORD = '3x0w0rks'
    MAIL_PASSWORD = 'vhvvqwokwpmcexdh' #Habilitamos en el correo la opcion contraseña de aplicacion
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False 
    
class DevelopmentConfig(Config):
    DEBUG=True
   
config = {
     'development': DevelopmentConfig
    }
    