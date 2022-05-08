from distutils.debug import DEBUG
from decouple import config
from flask import Config

class Config:
    SECRET_KEY=config('SECRET_KEY')
    
class DevelopmentConfig(Config):
    DEBUG=True
    
config = {
    'development': DevelopmentConfig
}
    