# app.py
import os
import re
from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, render_template, url_for, session, jsonify, request
from flask_expects_json import expects_json
from itsdangerous import NoneAlgorithm
#from flask_session import Session
from werkzeug.security import generate_password_hash,check_password_hash
from flask_mail import Mail, Message
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import CSRFProtect


#Importamos la configuracion del fichero config.py

from formularios import FormCambioPassword, FormRecupera, FormRegistro, FormLogin

from models.Modelo import Usuario, Empresa
from os import environ as env
from dotenv import load_dotenv

from auth import admin_required
from flask_jwt_extended import JWTManager

from flask_talisman import Talisman


mail = Mail()

talisman = Talisman()
csrf = CSRFProtect()

def fecha_actual():
    now = datetime.now()
    año = now.year
    mes = now.month
    dia = now.day
    return str(mes)+'/'+str(dia)+'/'+str(año)
   

def create_app():
    app = Flask(__name__)
    
    csp = {
        'default-src': ['*', 'unsafe-inline', 'strict-dynamic', 'unsafe-hashes', "'sha256-yVhOaSpFYsHuy4vwNVCVxs7R7CGIk8isIDt57LTu9Fo='"],
        'script-src': ['*', '\'self\'', "'nonce-2726c7f26c'", 'strict-dynamic', 'unsafe-inline'],
        'font-src': ['*', 'strict-dynamic', 'data:'],
        'img-src': ['*', 'data:', '\'self\''],   
    }
    
    talisman = Talisman(app, content_security_policy=csp)
    #Talisman(app, content_security_policy=[])
       
    app.jinja_env.globals.update(fecha_actual=fecha_actual)
    
    load_dotenv()
    
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config ['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config ['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config ['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config ['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config ['MAIL_USE_SSL'] = False
    app.config ['MAIL_USE_TLS'] = True
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = "pASSW0Rd"
    #Establecemos 10 minutos como tiempo de validez de los tokens de acceso a la API
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)

    jwt = JWTManager(app) 
    csrf = CSRFProtect(app) 
  
    #Session(app)
    
    #Aosciamos la BD con nuestra aplicacion
    from database.database import db
    
    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    #Creamos el objeto mail y lo inicializamos

    mail.init_app(app)
    csrf.init_app(app)
    
    
    def page_not_found(error):
        return "<h1> Not found page </h1>",404
    
    # Routes
    from routes import Controlador
       # Blueprints
       # Cuando accedamos a localhost/api/usuarios nos enlace con la ruta / del blueprint usuarios

    
    app.register_blueprint(Controlador.main, url_prefix='/api')
    #csrf.exempt(Controlador.main)
           
           #Manejador de errores
    app.register_error_handler(404, page_not_found)


    #Creamos una instancia de la clase LoginManager
    login_manager = LoginManager(app)
    
    #Creamos la vista a la que se redirige en caso de una ruta que requiere login previo
    #Redirigimos a la vista de login
    login_manager.login_view="login"
    
    @login_manager.user_loader
    def load_user(user_id):
        usuario = Controlador.Usuario.get_by_id(user_id)
        return usuario
    
    @app.route('/registro', methods=['GET'])
    def registro_get():
        form = FormRegistro()
        error = None
        
        return render_template("signup_form.html", form=form, error=error)

    @app.route('/registro', methods=['POST'])
    def registro():
        form = FormRegistro()
        error = None
        if form.validate_on_submit():
            nombre_empresa = form.empresa.data
            cif = form.cif.data
            plan = form.planContratado.data
            nombre = form.nombre.data
            apellidos = form.apellidos.data
            nif = form.nif.data
            tlf = form.tlf.data
            email = form.email.data
            emailRecuperacion = form.emailRecuperacion.data
            password = form.password.data
            estado = True
            idRol = 1
            idJornadaLaboral = 1

            user = Controlador.Usuario.get_by_login(email)
            empresa = Controlador.Empresa.get_by_cif(cif)
            
            if empresa is not None:
                error = 'La empresa ya existe en la aplicacion'
            elif user is not None:
                error = 'Email ya registrado en el sistema'
            else:
                empresa = Controlador.Empresa(nombre=nombre_empresa, cif=cif, planContratado=plan, numEmpleados=1)           
                empresa.save()
                idempresa = empresa.get_id_empresa()
                user = Controlador.Usuario(nombre=nombre, apellidos=apellidos ,login=email, tlf=tlf, nif=nif,
                                        emailRecuperacion= emailRecuperacion, estado=estado, idEmpresa=idempresa,idRol=idRol, idJornadaLaboral=idJornadaLaboral)    
                user.set_password(password)
                user.save()
                #enviamos el correo confirmando
                msg = Message("Registro UbuExoWorks", sender='ubuexoworks@gmail.com' ,recipients=[email])
                msg.html = '<p>Se ha completado el registro correctamente</p>' + '<p>Usuario: '+email+'</p>'
                mail.send(msg)
                            
                return redirect(url_for('home'))
        return render_template("signup_form.html", form=form, error=error)
        


    @app.route("/" )
    @login_required
    def home():
        #En el caso de que lleguemos aqui con un id de Empresa en la url actualizamos la variable de session.
        if request.args.get('idEmpresa') != None:
            session['idEmpresa']=request.args.get('idEmpresa')
       
        empresa = Controlador.Empresa.get_nombre_by_id(session['idEmpresa'])
        user = Controlador.Usuario.get_by_id(session['idUsuario'])
       
        if session['rol'] == 1 or session['rol'] == 0:
            return render_template("index.html", idUsuario = session['idUsuario'], idEmpresa = session['idEmpresa'], empresa = empresa)
        else:
            return render_template("empleado.html", usuario = user, idUsuario = session['idUsuario'], idEmpresa = session['idEmpresa'], empresa = empresa)
    
    @app.route("/admin" )
    @login_required
    @admin_required
    def admin():
        return render_template("admin.html", idUsuario = session['idUsuario'], is_Admin = True)
    
    @app.route('/cambiaPass', methods=['GET'])
    def cambia_pass_get():
        form = FormCambioPassword()
        error = NoneAlgorithm
        return render_template('cambiapass_form.html', form=form, error=error)   
    
    @app.route('/cambiaPass', methods=['POST'])
    @login_required
    def cambiaPass():
        form = FormCambioPassword()
        error = None
        user = current_user
        if request.method =='GET':
            form.email.data = user.login
        
        if request.method =='POST':
            if form.cancel.data:
                return redirect(url_for('home'))
            
        if form.validate_on_submit():
            email = form.email.data
            password_actual = form.passwordActual.data
            password = form.password.data
            password2 = form.password2.data
            
            if user.check_password(password_actual):
                user.set_password(password)
                user.save()
                return redirect(url_for('home'))
            form.passwordActual.errors.append("Contraseña actual incorrecta.")
        return render_template('cambiapass_form.html', form=form, error=error)
          
    @app.route("/login", methods=['get', 'post'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        
        form = FormLogin()
        error = None
        
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user = Controlador.Usuario.get_by_login(email)
            if user is not None and user.check_password(password):
                if user.is_admin():
                    print('Es un ADMINISTRADOR')
                    login_user(user)
                    session['idUsuario'] = user.idUsuario
                    session['username'] = user.get_login()
                    session['rol'] = user.idRol
                    return redirect(url_for("admin"))
                if user.check_habilitado():
                    login_user(user)
                    session['idUsuario'] = user.idUsuario
                    session['idEmpresa'] = user.get_id_empresa()
                    session['username'] = user.get_login()
                    session['rol'] = user.idRol
                    return redirect(url_for("home"))
                form.email.errors.append("Usuario deshabiliado, contacte con su administrador.")
            form.email.errors.append("Usuario o contraseña incorrectos.")
        return render_template('login_form.html', form=form, error=error)
    
    @app.route("/recupera", methods=['get', 'post'])
    def recuperar():
        form = FormRecupera()
        error = None
        
        if request.method =='POST':
            if form.cancel.data:
                return redirect(url_for('home'))
        
        if form.validate_on_submit():
            email = form.email.data
            user = Controlador.Usuario.get_by_login(email)
            if user is not None:
               return redirect(url_for('usuarios_blueprint.recovery_pass_web', email=email))
            form.email.errors.append("El usuario no existe.")
            return redirect(url_for('home'))
        return render_template('recuperapass_form.html', form=form, error=error)
    
    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("login"))    

    return app    