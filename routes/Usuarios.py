from lib2to3.pgen2 import token
from flask import Blueprint, jsonify, request
from flask_expects_json import expects_json
from werkzeug.security import check_password_hash

#from models.Usuarios import db
#from app import db
# Modelos
from models.Usuarios import Usuario

#from models.UsuariosModel import UsuarioModel


main = Blueprint('usuarios_blueprint', __name__)

prueba = Blueprint('prueba', __name__)

@prueba.errorhandler(404)
def not_found(e):
    return prueba.send_static_file('index.html')

@prueba.route('/')
def probando():
    return "PRobando Probando......"


@main.route('/usuario', methods=('GET', 'POST'))
def get_usuarios():
    try:
        #usuarios = Usuario.query.filter(Usuario.login.like('prueba@prueba.com')).first()
        
        
        usuarios = Usuario.get_by_login('alejandro@correo.com')
        
        return jsonify(usuarios.to_JSON())
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500
    
@main.route('/2')
def get_usuariios2():
    return "Mas pruebas"

@main.route('/login')
@expects_json()
def login():
    datos = request.get_json()
    
    password=datos.get('password','')
    if password == "":
        return jsonify(error = "username vacio"),400
    
    username=datos.get('login', '')
    if username == "":
        return jsonify(error = "login vacio"),400
    
    usuario = Usuario.get_by_login(username)
    
    if usuario is not None:
        if Usuario.check_password(usuario, password):        
            return jsonify(token="Token correcto"),200
        return jsonify(error="login o contraseña incorrecta"),300
    
