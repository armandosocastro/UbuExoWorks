# app.py
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

#Importamos la configuracion del fichero config.py
from config import config

# Routes
from routes import Usuarios


app = Flask(__name__, static_url_path='/')



def page_not_found(error):
    return "<h1> Not found page </h1>",404

db = SQLAlchemy(app)

_port = os.environ.get('PORT', 5000)


@app.route("/")
def home():
    return "Hello, Flask!"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.config.from_object(config['development'])
    
    # Blueprints
    # Cuando accedamos a localhost/api/usuarios nos enlace con la ruta / del blueprint usuarios
    #app.register_blueprint(Usuarios.main, url_prefix='/api/usuarios')
    app.register_blueprint(Usuarios.main, url_prefix='/api')
    #Manejador de errores
    app.register_error_handler(404, page_not_found)
    app.run(threaded=True, port=_port)