from flask import Blueprint, jsonify
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
        usuarios = Usuario.get_by_login('prueba@prueba.com')
        return jsonify(usuarios.to_JSON())
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500
    
@main.route('/2')
def get_usuariios2():
    return "Mas pruebas"
