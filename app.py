# app.py



import os
import re
from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, render_template, url_for, session, jsonify, request
from flask_expects_json import expects_json
#from flask_session import Session
from werkzeug.security import generate_password_hash,check_password_hash
from flask_mail import Mail, Message
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import CSRFProtect


#Importamos la configuracion del fichero config.py
#from config import config

from formularios import FormCambioPassword, FormRegistro, FormLogin
#from models.Usuarios import Usuario, Empresa
from models.Usuarios import Usuario, Empresa
from os import environ as env
from dotenv import load_dotenv

from auth import admin_required
from flask_jwt_extended import JWTManager

from flask_talisman import Talisman

mail = Mail()


def fecha_actual():
    now = datetime.now()
    año = now.year
    mes = now.month
    dia = now.day
    print("En fecha actual: ",mes,dia,año)
    return str(mes)+'/'+str(dia)+'/'+str(año)
   

#def create_app(settings_module='config.DevelopmentConfig'):
def create_app():
    app = Flask(__name__)
    feature_policy = {
        'force_https': True
    }
    Talisman(app, feature_policy=feature_policy)
    
    app.jinja_env.globals.update(fecha_actual=fecha_actual)
    
    load_dotenv()
    
    #app.config.from_object(settings_module)
    #app.config.from_envvar('SQLALCHEMY_DATABASE_URI')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config ['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config ['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config ['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config ['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config ['MAIL_USE_SSL'] = False
    app.config ['MAIL_USE_TLS'] = True
    app.config['SECRET_KEY'] = 'pASSW0Rd'
    app.config['JWT_SECRET_KEY'] = "pASSW0Rd"
    #Establecemos 10 minutos como tiempo de validez de los tokens de acceso a la API
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)

    jwt = JWTManager(app)
    
   #csrf = CSRFProtect()   
   
    #Session(app)
    
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
    #app.config.from_object(config['development'])
    
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
        
        usuario = Usuarios.Usuario.get_by_id(user_id)
        return usuario
    
    @app.route('/registro', methods=['GET', 'POST'])
    def registro():
        form = FormRegistro()
        error = None
        if form.validate_on_submit():
            nombre_empresa = form.empresa.data
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
            elif user is not None:
                error = 'Email ya registrado en el sistema'
            else:
                empresa = Usuarios.Empresa(nombre=nombre_empresa, cif=cif, planContratado=plan, numEmpleados=1)           
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
        


    @app.route("/" )
    @login_required
    def home():
        print('En home...con el usuario:', session['username'], session['idUsuario'], 'rol session:', session['rol'])
        #En el caso de que lleguemos aqui con un id de Empresa en la url actualizamos la variable de session.
        if request.args.get('idEmpresa') != None:
            session['idEmpresa']=request.args.get('idEmpresa')
        #print('empresa id: ',session['idEmpresa'])
        #return "Hello, Flask!"
        #listadoUsuarios = Usuarios.Usuario.get_by_empresa(session['idEmpresa'])
        empresa = Usuarios.Empresa.get_nombre_by_id(session['idEmpresa'])
        user = Usuarios.Usuario.get_by_id(session['idUsuario'])
        print('Usuario completo: ', user)
        #return render_template("index.html", usuarios=listadoUsuarios)
        if session['rol'] == 1:
            return render_template("index.html", idUsuario = session['idUsuario'], idEmpresa = session['idEmpresa'], empresa = empresa)
        else:
            return render_template("empleado.html", usuario = user, idUsuario = session['idUsuario'], idEmpresa = session['idEmpresa'], empresa = empresa)
    
    @app.route("/admin" )
    @login_required
    @admin_required
    def admin():
        print('En panel de Administracion...con el usuario:', session['username'], session['idUsuario'])
      
        #empresa = Usuarios.Empresa.get_nombre_by_id(session['idEmpresa'])
        empresas = Usuarios.Empresa.get_all()
        print('Listado de enmpresas: ', empresas)
        #return render_template("index.html", usuarios=listadoUsuarios)
        return render_template("admin.html", idUsuario = session['idUsuario'], is_Admin = True)
    
    @app.route('/cambiaPass', methods=['POST','GET'])
    @login_required
    def cambiaPass():
        form = FormCambioPassword()
        error = None
        #user = Usuarios.Usuario.get_by_login(email)
        user = current_user
        if request.method =='GET':
            form.email.data = user.login
            
        if form.validate_on_submit():
            email = form.email.data
            password_actual = form.passwordActual.data
            password = form.password.data
            password2 = form.password2.data
            
            if user.check_password(password_actual):
                print('La contraseña actual coincide..')
                user.set_password(password)
                user.save()
                return redirect(url_for('home'))
            form.passwordActual.errors.append("Contraseña actual incorrecta.")
        return render_template('cambiapass_form.html', form=form)
          
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
                if user.is_admin():
                    print('Es un ADMINISTRADOR')
                    login_user(user)
                    session['idUsuario'] = user.idUsuario
                    #session['idEmpresa'] = user.get_id_empresa()
                    session['username'] = user.get_login()
                    session['rol'] = user.idRol
                    return redirect(url_for("admin"))
                if user.check_habilitado():
                    print('por aqui no......')
                    login_user(user)
                    session['idUsuario'] = user.idUsuario
                    session['idEmpresa'] = user.get_id_empresa()
                    session['username'] = user.get_login()
                    session['rol'] = user.idRol
                    print('idempresa: ', session['idEmpresa'], session['username'], 'rol:', session['rol'])
                    return redirect(url_for("home"))
                form.email.errors.append("Usuario deshabiliado, contacte con su administrador.")
            form.email.errors.append("Usuario o contraseña incorrectos.")
        return render_template('login_form.html', form=form)
        #return render_template('login_register.html', form=form)

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("login"))    

    return app    