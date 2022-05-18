# app.py
import os
import re

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, render_template, url_for
from werkzeug.security import generate_password_hash,check_password_hash

#Importamos la configuracion del fichero config.py
from config import config

from formularios import FormRegistro
from models.Usuarios import Usuario


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
    
    @app.route('/registro', methods=['GET', 'POST'])
    def registro():
        form = FormRegistro()
        error = None
        if form.validate_on_submit():
            nombre = form.nombre.data
            apellidos = form.apellidos.data
            email = form.email.data
            password = form.password.data
            idempresa = 1
            estado = True
            idRol = 1
            print('email y pass: ', email, password)
            user = Usuarios.Usuario.get_by_login(email)
            if user is not None:
                error = f'Usuario ya existe'
            else:
                user = Usuarios.Usuario(nombre=nombre, apellidos=apellidos ,login=email, estado=estado,idEmpresa=idempresa,idRol=idRol)    
                user.set_password(password)
                user.save()
            return redirect(url_for('/'))
        return render_template("signup_form.html", form=form, error=error)
    
    
    def page_not_found(error):
        return "<h1> Not found page </h1>",404

    @app.route("/")
    def home():
        return "Hello, Flask!"
          
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