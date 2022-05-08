from flask import Blueprint, jsonify

# Modelos
from models.UsuariosModel import UsuarioModel


main = Blueprint('usuarios_blueprint', __name__)

@main.route('/')
def get_usuarios():
    try:
        usuarios = UsuarioModel.get_usuario()
        return jsonify(usuarios)
    except Exception as ex:
        return jsonify({'mensaje': str(ex)}), 500
    