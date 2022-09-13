
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
from app import talisman

#from app import csrf

main = Blueprint('usuarios_blueprint', __name__)


@main.errorhandler(404)
def not_found(e):
    return main.send_static_file('index.html')


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
 
#Metodo API devuelve los datos del usuario solicitado    
@main.route('/get/usuario', methods=['GET'])
@jwt_required()
def get_usuario():
    try:
        idUsuario = request.args.get('idUsuario')   
        usuario = Usuario.get_by_id(idUsuario)
        if usuario is not None:
            return jsonify(usuario.to_JSON()), 200
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500
    
#Metodo API solicitud borrado fichaje
@main.route('/usuario/solicitudBorrado', methods=['POST'])
@jwt_required()
def solicitud_borrar_fichaje():
    try:
        idUsuario = request.args.get('idUsuario')   
        idFichaje = request.args.get('idFichaje')
        fichaje = Fichaje.get_by_idFichaje(idFichaje)
        
        #Hay que localizar el email del gestor de la empres
        usuario = Usuario.get_by_id(idUsuario)
        idEmpresa = usuario.idEmpresa
        gestor = Usuario.get_gestor(idEmpresa)
        email= gestor.get_email()
        
        #enviamos el correo con la solicitud de borrado
        msg = Message("UbuExoWorks: Solicitud borrado de fichaje", sender='ubuexoworks@gmail.com' ,recipients=[email])
        msg.html = '<p>Se solicita el borrado del fichaje del dia ' + str(fichaje.fecha) + 'a las ' + str(fichaje.hora_entrada) + ' horas' + ' con el identificador ' + str(fichaje.idFichaje) + '</p>'
        mail.send(msg)
        return  jsonify('Ok'), 200
        
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

#Metodo API para registro del imei del dispositivo
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
            return jsonify("Ok"),200
        return jsonify("Contraseña incorrecta"),300
    return jsonify("No existe usuario"),300

#Login para la API, se comprueba que tambien tenga registrado el dispositivo
@main.route('/login', methods=['POST'])
@expects_json()
def login():
    datos = request.get_json()
   
    password=datos.get('password','')
    if password == "":
        return jsonify("password vacio"),400
    
    username=datos.get('login', '')
    if username == "":
        return jsonify("login vacio"),400
    
    imei=datos.get('imei', '')
    if imei == "":
        return jsonify("imei vacio"),400
    
    usuario = Usuario.get_by_login(username)
    
    secret = os.environ.get('SECRET_KEY') #sale del fichero .env
    print('secreto', secret)
    
    if usuario is not None:
        if Usuario.check_password(usuario, password):  
            if Usuario.check_imei(usuario, imei):      
                #Generamos el token a partir del id del usuario
                token = create_access_token(identity=usuario.idUsuario)
                idUsuario= usuario.idUsuario
                #return jsonify(token=usuario.idUsuario),200
                return jsonify(idUsuario=idUsuario,token=token),200
            else:
                return jsonify("dispositivo no registrado"), 300
        return jsonify("contraseña incorrecta"),300
    return jsonify("No existe usuario"),300

#Metodo para registrar un fichaje por el Gestor sin necesidad de tokens de seguridad
@main.route('/fichajeGestor', methods=['POST','GET'])
#@jwt_required()
@expects_json()
def fichajeGestor():
    try:
        #current_user_id = get_jwt_identity()
        datos = request.get_json()
        print(datos)
        #print('curren id fichaje:', current_user_id)

        idUsuario= datos.get('idUsuario','')
        fecha = datos.get('fecha','')
        hora = datos.get('hora','')
        longitud = datos.get('longitud','')
        latitud = datos.get('latitud','')
        tipo = datos.get('tipo','')
        incidencia = datos.get('incidencia','')
        
        entradas = 0
        pausas = 0

        fichajes_hoy = Fichaje.get_by_idEmpleadoFecha(idUsuario, fecha)
        for fichaje in fichajes_hoy:
            print('fichajes horas: ',(fichaje.hora_entrada).strftime("%H:%M"),' : ', hora)
            #No permitimos fichajes a la misma hora, debe transcurrir un minuto entre ellos
            if (fichaje.hora_entrada).strftime("%H:%M") == hora:
                return jsonify("solapado")
            if fichaje.tipo == 'entrada':
                entradas = entradas + 1
            elif fichaje.tipo == 'salida':
                    entradas = entradas -1
            elif fichaje.tipo == 'pausa entrada':
                pausas = pausas + 1
            else:
                pausas = pausas - 1

        if tipo == 'fichaje':

            if entradas % 2 == 0:
                tipo_fichaje = 'entrada'
            else:
                tipo_fichaje = 'salida'
        else:

            if pausas % 2 == 0:
                tipo_fichaje = 'pausa entrada'
            else:
                tipo_fichaje = 'pausa salida' 
        
        fichaje = Fichaje(fecha=fecha, hora_entrada=hora, entrada_longitud=longitud, entrada_latitud=latitud,
                          incidencia=incidencia,idUsuario=idUsuario, tipo=tipo_fichaje)
        fichaje.save()
        return jsonify(token="Ok"),200   
           
    except Exception as ex:
        print(ex)
        return 'JSON incorrecto', 400

#Metodo para borrado de fichaje por perfil Gestor
@main.route('/borrarFichaje', methods=['POST'])
@login_required
@gestor_required
def borrarFichajeGestor():
    try:
        idFichaje = request.args.get('idFichaje')
        print('fichaje a borrar: ',idFichaje)     

        fichaje = Fichaje.get_by_idFichaje(idFichaje)
        fichaje.borrado = True
        fichaje.save()
        
        return "ok"
    except Exception as ex:
        print(ex)
        return 'Peticion incorrecta'

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

        entradas = 0
        pausas = 0

        fichajes_hoy = Fichaje.get_by_idEmpleadoFecha(current_user_id, fecha)
        for fichaje in fichajes_hoy:
            print('fichajes horas: ',(fichaje.hora_entrada).strftime("%H:%M"),' : ', hora)
            #No permitimos fichajes a la misma hora, debe transcurrir un minuto entre ellos
            #En el caso de que este borrado no lo tenemos en cuenta
            if fichaje.borrado == False:
                if (fichaje.hora_entrada).strftime("%H:%M") == hora:
                    return jsonify(token="solapado"), 400
                if fichaje.tipo == 'entrada':
                    entradas = entradas + 1
                elif fichaje.tipo == 'salida':
                        entradas = entradas -1
                elif fichaje.tipo == 'pausa entrada':
                    pausas = pausas + 1
                else:
                    pausas = pausas - 1


        if tipo == 'fichaje':

            if entradas % 2 == 0:
                tipo_fichaje = 'entrada'
            else:
                tipo_fichaje = 'salida'
        else:
  
            if pausas % 2 == 0:
                tipo_fichaje = 'pausa entrada'
            else:
                tipo_fichaje = 'pausa salida' 
        
        if str(current_user_id) == str(idUsuario):
            fichaje = Fichaje(fecha=fecha, hora_entrada=hora, entrada_longitud=longitud, entrada_latitud=latitud,
                          incidencia=None,idUsuario=idUsuario, tipo=tipo_fichaje, borrado=False)
            fichaje.save()
            return jsonify(token="Ok"),200   
        else:
            return jsonify({"token incorrecto"}), 401
           
    except Exception as ex:
        print(ex)
        return 'JSON incorrecto', 400
    
#Metodo API para obtener todos los fichajes de un usuario    
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
            return jsonify({"token incorrecto"}), 401
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
            return jsonify({"token incorrecto"}), 401   
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500        
 
    
@main.route('/usuario/fichajes', methods=['get'])
@talisman()
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
    entrada = False
    if fichajes == []:
        #Devolvemos un diccionario vacio si no hay datos de gastos para enviar.
        return jsonify({'data':[]})
    else:
        data = []
        for f in fichajes:
            data.append({"ID":f.idFichaje, "fecha":f.fecha, "hora":str(f.hora_entrada), "tipo":f.tipo, "longitud":f.entrada_longitud, "latitud":f.entrada_latitud,
                              "incidencia":f.incidencia, "borrado":f.borrado})
            print('fichaje ajax:',data)
        data_json = {'data': data}
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
        data_json = {'data':[{"ID":f.idFichaje, "fecha":f.fecha, "hora":str(f.hora_entrada), "tipo":f.tipo, "longitud":f.entrada_longitud, "latitud":f.entrada_latitud,
                              "incidencia":f.incidencia, "borrado":f.borrado} for f in fichajes]} 
        return jsonify(data_json)
  
#Metodo API que devuelve los fichajes entre dos fechas       
@main.route('/usuario/fichajesRango', methods=['get','post'])
@jwt_required()
def usuarioFichajesRango():
    try:
        current_user_id = get_jwt_identity()
        idUsuario = request.args.get('idUsuario')
        fecha_ini = request.args.get('fecha_ini')
        fecha_fin = request.args.get('fecha_fin')
        print('::', idUsuario, fecha_fin, fecha_ini)
        if str(current_user_id) == str(idUsuario):
            fichajes = Fichaje.get_by_idEmpleadoRango(idUsuario, fecha_ini, fecha_fin)
            print('fichajes:', fichajes)
            if fichajes == []:
                #Devolvemos un diccionario vacio si no hay datos de gastos para enviar.
                return jsonify([fichaje.to_JSON() for fichaje in fichajes])
            else:
                return jsonify([fichaje.to_JSON() for fichaje in fichajes])
        else:
            return jsonify({'token incorrecto'}), 401
    except Exception as ex:
        return jsonify({ 'error': str(ex)}), 500


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

#Metodo API para registrar un gasto con su ticket
@main.route("/gasto/registraGasto", methods=['post'])
@jwt_required()
def registraGasto():
    try:
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
            imagen_string = base64.b64encode(imagen.read())
            
            gasto = Gasto(fecha=fecha, tipo=tipo, descripcion=descripcion, importe=importe, iva=iva, cif=cif,fotoTicket=imagen_string,idUsuario=idUsuario,razonSocial=razonSocial,numeroTicket=numeroTicket)
            gasto.save()
            
            return jsonify("Ok"), 200
    except Exception as ex:
        return jsonify({ 'error': str(ex)}), 500
        
   
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
     
    if gasto.validado == False:
        gasto.validado = True
    else:
        gasto.validado = False
    
    gasto.save()
    return "ok"


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
        emailRecuperacion = form.emailRecuperacion.datsa
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
            user = Usuario(nombre=nombre, apellidos=apellidos,nif=nif,login=email,emailRecuperacion=emailRecuperacion, estado=estado,idEmpresa=idempresa,idRol=idRol,idJornadaLaboral=idJornadaLaboral)
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

