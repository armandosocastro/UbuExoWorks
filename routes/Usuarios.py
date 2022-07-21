
#from crypt import methods

from lib2to3.pgen2 import token
from flask import Blueprint, jsonify, request, redirect, render_template, session, url_for
from flask_expects_json import expects_json
from werkzeug.security import check_password_hash
from flask_wtf import CSRFProtect

from flask_mail import Mail, Message
from flask_login import current_user, login_required


#from models.Usuarios import db
#from app import db
# Modelos
from models.Usuarios import Fichaje, Usuario, Empresa

from formularios import FormAlta, FormModifica

#from app import csrf


#from models.UsuariosModel import UsuarioModel

mail = Mail()

main = Blueprint('usuarios_blueprint', __name__)

prueba = Blueprint('prueba', __name__)

@prueba.errorhandler(404)
def not_found(e):
    return prueba.send_static_file('index.html')


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

@main.route('/login', methods=['POST'])
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
            return jsonify(token=usuario.idUsuario),200
        return jsonify(error="contraseña incorrecta"),300
    return jsonify(error="No existe usuario"),300

@main.route('/fichaje', methods=['POST','GET'])
@expects_json()
def fichar():
    try:
        datos = request.get_json()
        print(datos)

        idUsuario= datos.get('idUsuario','')
        fecha = datos.get('fecha','')
        hora = datos.get('hora','')
        longitud = datos.get('longitud','')
        latitud = datos.get('latitud','')
        
        print('Longitud recibida: ', longitud)
        print('latitud recibida: ', latitud)
        
        fichaje = Fichaje(fecha=fecha, hora_entrada=hora, entrada_longitud=longitud, entrada_latitud=latitud,
                          incidencia=None,idUsuario=idUsuario)
        fichaje.save()
        
        return jsonify(token="OK"),200
    except Exception as ex:
        print(ex)
        return 'JSON incorrecto'
    
#Metodo API para obtener los fichajes de un usuario    
@main.route('/get/fichajes', methods=['get'])
#@expects_json()
def getFichaje():
    try:
        #datos = request.get_json()
        #print(datos)
        
        
        #idUsuario = datos.get('idUsuario','')
        idUsuario = request.args.get('idUsuario')
        print('usuario: ',idUsuario)
        fichajes = Fichaje.get_by_idEmpleado(idUsuario)
        print(fichajes)
        
        return jsonify([fichaje.to_JSON() for fichaje in fichajes])
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500    
    
@main.route('/get/fichaje/fecha', methods=['get'])
#@expects_json()
def getFichajePorFecha():
    try:
        #datos = request.get_json()
        #print(datos)

        idUsuario = request.args.get('idUsuario')
        fecha = request.args.get('fecha')
        print('usuario: ',idUsuario)
        print('fecha fichaje: ',fecha)
        
        fichajes = Fichaje.get_by_idEmpleadoFecha(idUsuario,fecha)
        print(fichajes)
        
        return jsonify([fichaje.to_JSON() for fichaje in fichajes])
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500        
    
@main.route('/get/fichaje', methods=['get'])
@expects_json()
def getFichajeFecha():
    try:
        datos = request.get_json()
        print(datos)

        idUsuario = datos.get('idUsuario','')
        fecha = datos.get('fecha','')
        print('usuario: ',idUsuario)
        print('fecha fichaje: ',fecha)
        
        fichajes = Fichaje.get_by_idEmpleadoFecha(idUsuario,fecha)
        print(fichajes)
        
        return jsonify([fichaje.to_JSON() for fichaje in fichajes])
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500        
    
@main.route('/usuario/fichajes<idUsuario>', methods=['get'])
def usuarioFichajes(idUsuario):
    print('usuario: ',idUsuario)
    fichajes = Fichaje.get_by_idEmpleado(idUsuario)
    print(fichajes)
    return render_template('fichajes.html', listaFichajes=fichajes)

#Este metodo ya no lo utilizo
@main.route('/mapa<longitud><latitud>')
def mapa(longitud,latitud):
    #longitud=20.35235054304456
    #latitud=-8.402286665327859
    return render_template('mapa.html',longitud=longitud, latitud=latitud)
    
#Este metodo ya no lo utilizo    
@main.route("/ubicacion", methods=['post'])
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
   
@main.route('/alta', methods=['get', 'post'])
@login_required
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
            print("Creado usuario")
            #enviamos el correo confirmando

            msg = Message("Registro UbuExoWorks", sender='ubuexoworks@gmail.com' ,recipients=[email])
            msg.html = '<p>Se ha completado el registro correctamente</p>' + '<p>Usuario: '+email+'</p>' + '<p>Contraseña: '+password+'</p>'
            mail.send(msg)

            return redirect(url_for('home'))
    return render_template("alta.html", form=form, error=error)    
        

        
@main.route('/usuario/modifica<idUsuario>', methods=['get', 'post'])
@login_required
def modifica_usuario(idUsuario):
    print("en modificaciones")
    form = FormModifica()
    error = None
    user = Usuario.get_by_id(idUsuario)
    
    if request.method =='GET':
        form.nombre.data = user.nombre
        form.apellidos.data = user.apellidos
        form.nif.data = user.nif
        form.email.data = user.login
        form.estado.data = user.estado
        
    if form.validate_on_submit():
        user.nombre = form.nombre.data
        user.apellidos = form.apellidos.data
        user.nif = form.nif.data
        user.email = form.email.data
        #password = form.password.data
        #idempresa=current_user.
        idempresa = session['idEmpresa']
        #estado = True
        user.estado = form.estado.data
        idRol = 1
        idJornadaLaboral = 1
        #numEmpleados = 1

        #print('email y pass: ', email, password)
        #user = Usuario.get_by_login(email)
        #user = Usuario.get_by_id(idUsuario)
        #empresa = Usuarios.Empresa.get_by_cif(cif)

        #if user is not None:
        #    error = 'El usuario ya esta registrado en el sistema'
        #else:
            #user = Usuario(nombre=nombre, apellidos=apellidos,nif=nif,login=email,estado=estado,idEmpresa=idempresa,idRol=idRol,idJornadaLaboral=idJornadaLaboral)
        user.save()
        
            #password = Usuario.generate_password()
            #user.set_password(password)
            #user
            #user.save()
        print("Modificado usuario")
            #enviamos el correo confirmando

            #msg = Message("Registro UbuExoWorks", sender='ubuexoworks@gmail.com' ,recipients=[email])
            #msg.html = '<p>Se ha completado el registro correctamente</p>' + '<p>Usuario: '+email+'</p>' + '<p>Contraseña: '+password+'</p>'
            #mail.send(msg)

        return redirect(url_for('home'))
    return render_template("modifica.html", form=form, error=error)    
        
