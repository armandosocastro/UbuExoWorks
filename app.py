# app.py



import os
import re

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, render_template, url_for, session, jsonify, request
from flask_expects_json import expects_json
#from flask_session import Session
from werkzeug.security import generate_password_hash,check_password_hash
from flask_mail import Mail, Message
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import CSRFProtect


#Importamos la configuracion del fichero config.py
from config import config

from formularios import FormRegistro, FormLogin
#from models.Usuarios import Usuario, Empresa
from models.Usuarios import Usuario, Empresa

mail = Mail()


def create_app():

    app = Flask(__name__)
    
   #csrf = CSRFProtect()

    app.config ['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config ['MAIL_PORT'] = 587
    app.config ['MAIL_USERNAME'] = 'ubuexoworks@gmail.com'
    app.config ['MAIL_PASSWORD'] = '3x0w0rks'
    app.config ['MAIL_USE_SSL'] = False
    app.config ['MAIL_USE_TLS'] = True
    app.config['SECRET_KEY'] = 'pASSW0Rd'
    
    #Session(app)
    
    #print('servidor:' ,os.environ.get('MAIL_SERVER'))
    
    #Aosciamos la BD con nuestra aplicacion
    from database.database import db
    #db = SQLAlchemy(app)
    
    #uri = os.getenv("DATABASE_URL")
    #if uri.startswith("postgres://"):
    #    uri = uri.replace("postgres://", "postgresql://", 1)
    

    
    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    #Creamos el objeto mail y lo inicializamos

    mail.init_app(app)
    
     #if __name__ == '__main__':
    #Threaded option to enable multiple instances for multiple user access support
    app.config.from_object(config['development'])
    
    def page_not_found(error):
        return "<h1> Not found page </h1>",404
    
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

    #Creamos una instancia de la clase LoginManager
    login_manager = LoginManager(app)
    
    #Creamos la vista a la que se redirige en caso de una ruta que requiere login previo
    #Redirigimos a la vista de login
    login_manager.login_view="login"
    
    @login_manager.user_loader
    def load_user(user_id):
        #return Usuarios.Usuario.query.get(int(user_id))
        print ("Usuario que se intenta logear: ", user_id)
        return Usuarios.Usuario.get_by_id(user_id)
    
    @app.route('/registro', methods=['GET', 'POST'])
    def registro():
        form = FormRegistro()
        error = None
        if form.validate_on_submit():
            empresa = form.empresa.data
            cif = form.cif.data
            plan = form.planContratado.data
            nombre = form.nombre.data
            apellidos = form.apellidos.data
            email = form.email.data
            password = form.password.data
            #idempresa = 1
            estado = True
            idRol = 1
            idJornadaLaboral = 1
            #numEmpleados = 1
            
            print('email y pass: ', email, password)
            user = Usuarios.Usuario.get_by_login(email)
            empresa = Usuarios.Empresa.get_by_cif(cif)
            
            if empresa is not None:
                error = 'La empresa ya existe en la aplicacion'
            else:
                empresa = Usuarios.Empresa(nombre=nombre, cif=cif, planContratado=plan, numEmpleados=1)
                
                
                empresa.save()
                idempresa = empresa.get_id_empresa()
                print('emrpesa: ', idempresa)
                user = Usuarios.Usuario(nombre=nombre, apellidos=apellidos ,login=email, estado=estado, idEmpresa=idempresa,idRol=idRol, idJornadaLaboral=idJornadaLaboral)    
                user.set_password(password)
                user.save()
                
                #enviamos el correo confirmando
                
                msg = Message("Registro UbuExoWorks", sender='ubuexoworks@gmail.com' ,recipients=[email])
                msg.html = '<p>Se ha completado el registro correctamente</p>' + '<p>Usuario: '+email+'</p>'
                mail.send(msg)
                            
                return redirect(url_for('home'))
        return render_template("signup_form.html", form=form, error=error)
    
    
    @app.route("/ubicacion", methods=['post'])
    @expects_json()
    def ubicacion():
        try:
            datos = request.get_json()
            print(datos)

            longitud = datos.get('longitud','')
            latitud = datos.get('latitud','')

            print('Longitud recibida: ', longitud)
            print('latitud recibida: ', latitud)

            return jsonify(token="OK"),200
        except Exception as ex:
            return jsonify({'mensaje': str(ex)}), 500     


    @app.route("/" )
    @login_required
    def home():
        
       #return "Hello, Flask!"
        listadoUsuarios = Usuarios.Usuario.get_by_empresa(session['idEmpresa'])
        return render_template("index.html", usuarios=listadoUsuarios)
          
    @app.route("/login", methods=['get', 'post'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        
        form = FormLogin()
        error = None
        
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user = Usuarios.Usuario.get_by_login(email)
            if user is not None and user.check_password(password):
                login_user(user)
                session['idEmpresa'] = user.get_id_empresa()
                session['username'] = user.get_login()
                print('idempresa: ', session['idEmpresa'])
                return redirect(url_for("home"))
            form.email.errors.append("Usuario o contraseña incorrectos.")
        return render_template('login_form.html', form=form)
        #return render_template('login_register.html', form=form)
     
    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("login"))            
        
   
   
   
                

    return app    