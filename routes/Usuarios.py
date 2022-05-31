


from lib2to3.pgen2 import token
from flask import Blueprint, jsonify, request, redirect, render_template, session, url_for
from flask_expects_json import expects_json
from werkzeug.security import check_password_hash
from flask_wtf import CSRFProtect

from flask_mail import Mail, Message
from flask_login import current_user


#from models.Usuarios import db
#from app import db
# Modelos
from models.Usuarios import Usuario, Empresa

from formularios import FormAlta

#from app import csrf


#from models.UsuariosModel import UsuarioModel

mail = Mail()

main = Blueprint('usuarios_blueprint', __name__)

prueba = Blueprint('prueba', __name__)

@prueba.errorhandler(404)
def not_found(e):
    return prueba.send_static_file('index.html')

@prueba.route('/')
def probando():
    return "PRobando Probando......"


@main.route('/usuario', methods=('GET', 'POST'))
@expects_json()
def get_usuarios():
    try:
        #usuarios = Usuario.query.filter(Usuario.login.like('prueba@prueba.com')).first()
        datos=request.get_json()
        usuario = datos.get('login','')
        
        usuarios = Usuario.get_by_login(usuario)
        
        return jsonify(usuarios.to_JSON())
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500

@main.route('/login')
@expects_json()
def login():
    datos = request.get_json()
   
    password=datos.get('password','')
    if password == "":
        return jsonify(error = "password vacio"),400
    
    username=datos.get('login', '')
    if username == "":
        return jsonify(error = "login vacio"),400
    
    usuario = Usuario.get_by_login(username)
    
    if usuario is not None:
        if Usuario.check_password(usuario, password):        
            return jsonify(token="OK"),200
        return jsonify(error="contraseña incorrecta"),300
    return jsonify(error="No existe usuario"),300

#@csrf.exempt
@main.route('/ubicacion', methods=['POST','GET'])
@expects_json
def ubicacion():
    """try:
        datos = request.get_json()
        print(datos)
    
        longitud = datos.get('longitud','')
        latitud = datos.get('latitud','')
    
        print('Longitud recibida: ', longitud)
        print('latitud recibida: ', latitud)
    
        return jsonify(token="OK"),200
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500 """
    return 'Esto es un JSON'
    
@main.route('/alta', methods=['get', 'post'])
def alta_usuario():
    print("en altas")
    form = FormAlta()
    error = None
    
    if form.validate_on_submit():
        nombre = form.nombre.data
        apellidos = form.apellidos.data
        nif = form.nif.data
        email = form.email.data
        #password = form.password.data
        #idempresa=current_user.
        idempresa = session['idEmpresa']
        estado = True
        idRol = 1
        idJornadaLaboral = 1
        #numEmpleados = 1

        #print('email y pass: ', email, password)
        user = Usuario.get_by_login(email)
        #empresa = Usuarios.Empresa.get_by_cif(cif)

        if user is not None:
            error = 'El usuario ya esta registrado en el sistema'
        else:
            user = Usuario(nombre=nombre, apellidos=apellidos,nif=nif,login=email,estado=estado,idEmpresa=idempresa,idRol=idRol,idJornadaLaboral=idJornadaLaboral)
            password = Usuario.generate_password()
            user.set_password(password)
            user.save()

            #enviamos el correo confirmando

            msg = Message("Registro UbuExoWorks", sender='ubuexoworks@gmail.com' ,recipients=[email])
            msg.html = '<p>Se ha completado el registro correctamente</p>' + '<p>Usuario: '+email+'</p>' + '<p>Contraseña: '+password+'</p>'
            mail.send(msg)

            return redirect(url_for('home'))
    return render_template("alta.html", form=form, error=error)    
        
