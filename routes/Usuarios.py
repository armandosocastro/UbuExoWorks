from flask import Blueprint, jsonify

# Modelos
from models.UsuariosModel import UsuarioModel


main = Blueprint('usuarios_blueprint', __name__)

prueba = Blueprint('prueba', __name__)

@prueba.errorhandler(404)
def not_found(e):
    return prueba.send_static_file('index.html')

@prueba.route('/')
def probando():
    return "PRobando Probando......"


@main.route('/', methods=('GET', 'POST'))
def get_usuarios():
    try:
        usuarios = UsuarioModel.get_usuario()
        return jsonify(usuarios)
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500
    
@main.route('/2')
def get_usuariios2():
    return "Mas pruebas"
