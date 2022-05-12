from distutils.debug import DEBUG
from decouple import config
from flask import Config

class Config:
    SECRET_KEY=config('SECRET_KEY')
    #SQLALCHEMY_DATABASE_URI = 'postgresql://adminDB:3x0w0rks@localhost:5432/DBexoWorks'
    SQLALCHEMY_DATABASE_URI = 'postgres://kbeqwsfgqwkxui:5f7c44f61a7f07badb4c9744daa1f5c5c3763b1eaf83dd5a277c5547bec1899e@ec2-3-231-82-226.compute-1.amazonaws.com:5432/dfdt60gdue5iln'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = 'https://miubuapp.herokuapp.com/'
    
class DevelopmentConfig(Config):
    DEBUG=True
    
config = {
    'development': DevelopmentConfig
}
    