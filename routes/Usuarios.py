
#from crypt import methods

from datetime import datetime
from fileinput import filename
from itertools import count
from lib2to3.pgen2 import token
from time import process_time_ns
from flask import Blueprint, jsonify, request, redirect, render_template, session, url_for
from flask_expects_json import expects_json
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf import CSRFProtect

from flask_mail import Mail, Message
from flask_login import current_user, login_required


#from models.Usuarios import db
#from app import db
# Modelos
from models.Usuarios import Fichaje, Gasto, Usuario, Empresa, Rol

from formularios import FormAlta, FormModifica
import os #Quitar despues de las prubeas con los tickets

import base64 #Para codificar/descodificar las imagenes

from auth import admin_required, gestor_required
import jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app import mail

#from app import csrf


#from models.UsuariosModel import UsuarioModel

#mail = Mail()



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

@main.route('/empresasAjax', methods=['get','post'])
def empresasAjax():
    #datos = request.get_data()
    #parametro = request.form
    #idUsuario = parametro['idUsuario']
    listadoEmpresas = Empresa.get_all()
    #roles = Rol.get_by_Rol()
    #fecha = parametro['fecha']
    print('listado empresas: ',listadoEmpresas)
    
    if listadoEmpresas == []:
        #Devolvemos un diccionario vacio si no hay empresas.
        return jsonify({'data':[]})
    else:
        data_json = {'data':[{"id":e.idEmpresa, "nombre":e.nombre, "cif":e.cif, "plancontratado":e.planContratado} for e in listadoEmpresas]} 
        return jsonify(data_json)
    
@main.route('/usuariosEmpresaAjax', methods=['get','post'])
def usuariosEmpresaAjax():
    #datos = request.get_data()
    #parametro = request.form
    #idUsuario = parametro['idUsuario']
    listadoUsuarios = Usuario.get_by_empresa(session['idEmpresa'])
    roles = Rol.get_by_Rol()
    #fecha = parametro['fecha']
    print('listado usuarios empresa: ',listadoUsuarios)
    
    if listadoUsuarios == []:
        #Devolvemos un diccionario vacio si no hay datos de gastos para enviar.
        return jsonify({'data':[]})
    else:
        data_json = {'data':[{"id":u.idUsuario, "nombre":u.nombre, "apellidos":u.apellidos, "email":u.login, "nif":u.nif, "rol":Rol.get_by_idRol(u.idRol),
                              "estado":u.estado} for u in listadoUsuarios]} 
        return jsonify(data_json)

@main.route('/registraDispositivo', methods=['POST'])
@expects_json()
def registraDispositivo():
    datos = request.get_json()
    
    password=datos.get('password','')
    if password == "":
        return jsonify(error = "password vacio"),400
    
    username=datos.get('login', '')
    if username == "":
        return jsonify(error = "login vacio"),400
    
    imei=datos.get('imei', '')
    if imei == "":
        return jsonify(error = "imei vacio"),400
    
    usuario = Usuario.get_by_login(username)
    
    if usuario is not None:
        if Usuario.check_password(usuario, password):  
            Usuario.registra_imei(usuario,imei)
            usuario.save()
            return jsonify(token="OK"),200
        return jsonify(error="contraseña incorrecta"),300
    return jsonify(error="No existe usuario"),300

#Login para la API, se comprueba que tambien tenga registrado el dispositivo
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
    
    imei=datos.get('imei', '')
    if imei == "":
        return jsonify(error = "imei vacio"),400
    
    usuario = Usuario.get_by_login(username)
    
    secret = os.environ.get('SECRET_KEY') #sale del fichero .env
    print('secreto', secret)
    
    if usuario is not None:
        if Usuario.check_password(usuario, password):  
            if Usuario.check_imei(usuario, imei):      
                #Generamos el token a partir del id del usuario
                token = create_access_token(identity=usuario.idUsuario)
                #return jsonify(token=usuario.idUsuario),200
                return jsonify(token),200
            else:
                return jsonify(error="dispositivo no registrado"), 300
        return jsonify(error="contraseña incorrecta"),300
    return jsonify(error="No existe usuario"),300


#Metodo API para registrar un fichaje
@main.route('/fichaje', methods=['POST','GET'])
@jwt_required()
@expects_json()
def fichar():
    try:
        current_user_id = get_jwt_identity()
        datos = request.get_json()
        print(datos)
        print('curren id fichaje:', current_user_id)

        idUsuario= datos.get('idUsuario','')
        fecha = datos.get('fecha','')
        hora = datos.get('hora','')
        longitud = datos.get('longitud','')
        latitud = datos.get('latitud','')
        tipo = datos.get('tipo','')
        
        print('Longitud recibida: ', longitud)
        print('latitud recibida: ', latitud)
        print('usuario recibido: ',idUsuario)
        fichajes_hoy = Fichaje.get_by_idEmpleadoFecha(current_user_id, fecha)
        for fichaje in fichajes_hoy:
            print('fichajes horas: ',(fichaje.hora_entrada).strftime("%H:%M"),' : ', hora)
            #No permitimos fichajes a la misma hora, debe transcurrir un minuto entre ellos
            if (fichaje.hora_entrada).strftime("%H:%M") == hora:
                return jsonify(token="solapado"), 500

        print('Numero fichajes hoy: ', len(fichajes_hoy))
        
        if str(current_user_id) == str(idUsuario):
            fichaje = Fichaje(fecha=fecha, hora_entrada=hora, entrada_longitud=longitud, entrada_latitud=latitud,
                          incidencia=None,idUsuario=idUsuario, tipo=tipo)
            fichaje.save()
            return jsonify(token="OK"),200   
        else:
            return jsonify({'mensaje': "token incorrecto"}), 500
           
    except Exception as ex:
        print(ex)
        return 'JSON incorrecto'
    
#Metodo API para obtener los fichajes de un usuario    
@main.route('/get/fichajes', methods=['get'])
@jwt_required()
#@expects_json()
def getFichaje():
    try:
        current_user_id = get_jwt_identity()
        print('current id:', current_user_id)
    
        idUsuario = request.args.get('idUsuario')
        print('usuario: ',idUsuario)
        if str(current_user_id) == str(idUsuario):
            fichajes = Fichaje.get_by_idEmpleado(idUsuario)
            print(fichajes)
            return jsonify([fichaje.to_JSON() for fichaje in fichajes])
        else:
            return jsonify({'mensaje': "token incorrecto"}), 500
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500    
    
    
#Metodo API para obtener los fichajes de un usuario formateado para el Fullcalendar   
#Rellenamos todos los fichajes del año actual
@main.route('/get/fichajesCalendario', methods=['get'])
#@expects_json()
def getFichajeCalendario():
    try:
        list_fichajes = []
        idUsuario = request.args.get('idUsuario')
        fecha = request.args.get('fecha')
        print('usuario: ',idUsuario, 'fecha:',fecha)
        
        
        fichajes = Fichaje.get_by_idEmpleadoAno(idUsuario,fecha)
        #print(fichajes)
        for fichaje in fichajes:
            fecha = fichaje.fecha.strftime('%Y-%m-%d')
            #print("fecha: ", fecha)
            dict_fichajes = {'title': 'Dia fichado', 'start': fecha , 'end': fecha }
            list_fichajes.append(dict_fichajes)
        return jsonify(list_fichajes)
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500        
 
#Metodo para la API devuelve los fichajes de una fecha concreta  
@main.route('/get/fichaje', methods=['get'])
@jwt_required()
#@expects_json()
def getFichajePorFecha():
    try:
        current_user_id = get_jwt_identity()
        print('current id:', current_user_id)
        #datos = request.get_json()
        #print(datos)

        idUsuario = request.args.get('idUsuario')
        fecha = request.args.get('fecha')
        print('usuario: ',idUsuario)
        print('fecha fichaje: ',fecha)
        
        if str(current_user_id) == str(idUsuario):
            fichajes = Fichaje.get_by_idEmpleadoFecha(idUsuario,fecha)
            print(fichajes)
            return jsonify([fichaje.to_JSON() for fichaje in fichajes])
        else:
            return jsonify({'mensaje': "token incorrecto"}), 500   
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500        
 
    
@main.route('/usuario/fichajes', methods=['get'])
def usuarioFichajes():
    #datos = request.get_data()
    idUsuario = request.args.get('idUsuario')
    fecha = request.args.get('fecha')
    print('usuario: ',idUsuario)
    print('fehcha actual pasada: ',fecha)
    #fichajes = Fichaje.get_by_idEmpleado(idUsuario)
    fichajes = Fichaje.get_by_idEmpleadoFecha(idUsuario, fecha)
    print(fichajes)
    return render_template('fichajes.html', listaFichajes=fichajes, fechaHoy=fecha, idUsuario=idUsuario)

@main.route('/usuario/fichajesAjax', methods=['get','post'])
def usuarioFichajesAjax():
    #datos = request.get_data()
    parametro = request.form
    idUsuario = parametro['idUsuario']
    fecha = parametro['fecha']
    print('id: ',idUsuario, parametro)
    
    #idUsuario = request.args.get('idUsuario')
    #fecha = request.args.get('fecha')
    print('usuario ajax: ',idUsuario)
    print('fehcha actual pasada ajax: ',fecha)
    #fichajes = Fichaje.get_by_idEmpleado(idUsuario)
    fichajes = Fichaje.get_by_idEmpleadoFecha(idUsuario, fecha)
    #print('fichajes ajax:',fichajes)
    
    if fichajes == []:
        #Devolvemos un diccionario vacio si no hay datos de gastos para enviar.
        return jsonify({'data':[]})
    else:
        data_json = {'data':[{"fecha":f.fecha, "hora":str(f.hora_entrada), "tipo":f.tipo, "longitud":f.entrada_longitud, "latitud":f.entrada_latitud,
                              "incidencia":f.incidencia} for f in fichajes]} 
        return jsonify(data_json)
    
    #return render_template('fichajes.html', listaFichajes=fichajes, fechaHoy=fecha)
    
@main.route('/usuario/fichajesRangoAjax', methods=['get','post'])
def usuarioFichajesRangoAjax():
    parametro = request.form
    idUsuario = parametro['idUsuario']
    fecha_ini = parametro['fecha_ini']
    fecha_fin = parametro['fecha_fin']
  
    fichajes = Fichaje.get_by_idEmpleadoRango(idUsuario, fecha_ini, fecha_fin)
    
    if fichajes == []:
        #Devolvemos un diccionario vacio si no hay datos de gastos para enviar.
        return jsonify({'data':[]})
    else:
        data_json = {'data':[{"fecha":f.fecha, "hora":str(f.hora_entrada), "tipo":f.tipo, "longitud":f.entrada_longitud, "latitud":f.entrada_latitud,
                              "incidencia":f.incidencia} for f in fichajes]} 
        return jsonify(data_json)
        

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

#Metodo para obtener los gastos de un usuario en la aplicacion Web
@main.route('/usuario/gastos', methods=['get'])
def usuarioGastos():
    idUsuario = request.args.get('idUsuario')
    
    gastos = Gasto.get_by_idEmpleado(idUsuario)
    print('Gastos: ', gastos)
    return render_template('gastosAjax.html', listaGastos=gastos, idUsuario=idUsuario)

#metodo para devolver los tickets para peticion AJAX
@main.route('/ajax/cargatickets', methods=['get','post'])
def ajaxCargaTickets():
    parametro = request.form
    idUsuario = parametro['idUsuario']
    print('id: ',idUsuario, parametro)
    
    gastos = Gasto.get_by_idEmpleado(idUsuario)
    print('Gastos para ajax: ', gastos)
    if gastos == []:
        #Devolvemos un diccionario vacio si no hay datos de gastos para enviar.
        return jsonify({'data':[]})
    else:
        data_json = {'data':[{"ID":g.idGasto, "idUsuario":g.idUsuario, "fecha":g.fecha, "tipo":g.tipo, "razonsocial":g.razonSocial, "importe":g.importe,
                          "iva":g.iva, "cif":g.cif, "numeroticket":g.numeroTicket, "validado":g.validado} for g in gastos]} 
        return jsonify(data_json)

@main.route("/gasto/registraGasto", methods=['post'])
@jwt_required()
def registraGasto():
    if request.method == 'POST':
        
        idUsuario = request.form['idUsuario']
        fecha = request.form['fecha']
        tipo = request.form['tipo']
        importe = request.form['importe']
        iva = request.form['iva']
        cif = request.form['cif']
        razonSocial = request.form['razonSocial']
        descripcion = request.form['descripcion']
        numeroTicket = request.form['numeroTicket']
        
        imagen = request.files['ticket']
        #filename = secure_filename(imagen.filename)
        #imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagen_string = base64.b64encode(imagen.read())

        print(idUsuario)
        print(fecha)
        print(tipo)
        print(importe)
        print(iva)
        print(cif)
        print(razonSocial)
        print(descripcion)
        print(numeroTicket)
        
        gasto = Gasto(fecha=fecha, tipo=tipo, descripcion=descripcion, importe=importe, iva=iva, cif=cif,fotoTicket=imagen_string,idUsuario=idUsuario,razonSocial=razonSocial,numeroTicket=numeroTicket)
        gasto.save()
        
        return "Recibido ticket"
        
   
@main.route("/cargaTicket", methods=['get'])
def cargaTicket():
    idGasto = request.args.get('idGasto')
    
    gasto = Gasto.get_by_idGasto(idGasto)
    
    print('idGasto: ',idGasto, gasto.importe)
    imagen = base64.b64decode(gasto.fotoTicket)
    
    return imagen   


@main.route("/validaTicket", methods=['POST'])
@login_required
def validaTicket():
    
    idGasto = request.form['idGasto']
    #idGasto = request.args.get('idGasto')

    gasto = Gasto.get_by_idGasto(idGasto)
    
    print('idGasto a validar: ', idGasto)
     
    #print(request.form)
    if gasto.validado == False:
        gasto.validado = True
    else:
        gasto.validado = False
    
    gasto.save()
    return "ok"
    #return redirect(url_for('usuarios_blueprint.usuarioGastos', idUsuario = gasto.idUsuario))

@main.route("/validaTickets", methods=['post','get'])
def validaTickets():

    print('tickets validados:', request.form);
    for i in request.form:
        print(request.form['aprobar'])
    return "true"

@main.route('/alta', methods=['get', 'post'])
@login_required
@gestor_required
def alta_usuario():
    print("en altas")
    form = FormAlta()
    form.rol.choices = [(rol.idRol, rol.nombreRol) for rol in Rol.query.all()]
    print('roles select: ', form.rol.choices)
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
        idRol = form.rol.data
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
        
@main.route('usuario/recuperaPassword', methods=['get'])
def recoveryPass():
    idUsuario = request.args.get('idUsuario')
    print('El usuario: ', idUsuario, ' esta intentando recuperar la pass.')
    user = Usuario.get_by_id(idUsuario)
    if user is None:
        return "Error: el usuario no existe."
    else: 
        email = user.emailRecuperacion
        if email is None:
            return "Error: no hay email de recuperacion."
        else:
            passnueva = Usuario.generate_password()
            user.set_password(passnueva)
            user.save()
            print("Password regenerada enviada al correo ", email)
            #enviamos el correo confirmando

            msg = Message("Recuperacion contraseña UbuExoWorks", sender='ubuexoworks@gmail.com' ,recipients=[email])
            msg.html = '<p>Se ha generado una nueva contraseña de acceso</p>' + '<p>Usuario: '+email+'</p>' + '<p>Contraseña: '+passnueva+'</p>'
            mail.send(msg)            
            return "OK"
    
        
@main.route('/usuario/modifica', methods=['get', 'post'])
@login_required
@gestor_required
def modifica_usuario():
    form = FormModifica()
    form.rol.choices = [(rol.idRol, rol.nombreRol) for rol in Rol.query.all()]
    error = None
    idUsuario = request.args.get('idUsuario')
    idEmpresa = session['idEmpresa']
    print('EMPRESAID:', idEmpresa)
    user = Usuario.get_by_id(idUsuario)
    if request.method =='GET':
        form.nombre.data = user.nombre
        form.apellidos.data = user.apellidos
        form.nif.data = user.nif
        form.email.data = user.login
        form.rol.data = user.idRol
        form.estado.data = user.estado
        
    if form.validate_on_submit():
        print(request.form)
        
        if request.form['accion'] == 'Borrado':
            user.delete()
        else:
            if request.form['accion'] == 'Modificar':
                user.nombre = form.nombre.data
                user.apellidos = form.apellidos.data
                user.nif = form.nif.data
                user.email = form.email.data
                #password = form.password.data
                #idempresa=current_user.
                idempresa = session['idEmpresa']
                #estado = True
                user.estado = form.estado.data
                user.idRol = form.rol.data
                idJornadaLaboral = 1
                user.save()  
        return redirect(url_for('home', idEmpresa=idEmpresa))
    return render_template("modifica.html", form=form, error=error)    

