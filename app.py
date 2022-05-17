# app.py
import os
import re

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from werkzeug.security import generate_password_hash,check_password_hash

#Importamos la configuracion del fichero config.py
from config import config



def create_app():

    app = Flask(__name__)

    #Aosciamos la BD con nuestra aplicacion
    from database.database import db
    #db = SQLAlchemy(app)
    
    #uri = os.getenv("DATABASE_URL")
    #if uri.startswith("postgres://"):
    #    uri = uri.replace("postgres://", "postgresql://", 1)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    
    def page_not_found(error):
        return "<h1> Not found page </h1>",404

    @app.route("/")
    def home():
        return "Hello, Flask!"
    
    @app.route('/rutas')
    def muestra_rutas():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append('%s' % rule)
        return print(routes)
    
    #if __name__ == '__main__':
       # Threaded option to enable multiple instances for multiple user access support
    app.config.from_object(config['development'])
    
    # Routes
    from routes import Usuarios
       # Blueprints
       # Cuando accedamos a localhost/api/usuarios nos enlace con la ruta / del blueprint usuarios
       #app.register_blueprint(Usuarios.main, url_prefix='/api/usuarios')
    app.register_blueprint(Usuarios.prueba, url_prefix='/prueba')
    app.register_blueprint(Usuarios.main, url_prefix='/api')
   
           #Manejador de errores
    app.register_error_handler(404, page_not_found)
           #app.run(host='0.0.0.0', port=_port)
    
            
    return app    