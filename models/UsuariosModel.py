
from database.db import get_connection
from .entities.Usuarios import Usuario

class UsuarioModel():
    
    @classmethod  #Metodo de clase para llamarlo sin instanciar la clase
    def get_usuario(self):
        
        try:
            connection=get_connection()
            usuarios=[]
            
            with connection.cursor() as cursor:
                cursor.execute('SELECT "idUsuario", nombre, apellidos, login, password, estado, "idEmpresa", "idJornadaLaboral", "idRol" FROM "USUARIO" ')
                #cursor.execute('SELECT "idEmpresa" FROM "USUARIO"')
                #cursor.execute('SELECT * FROM "EMPRESA"')
                resultset = cursor.fetchall()
        
                for row in resultset:
                    usuario=Usuario(row[0],row[1], row[2],row[3],row[4],row[5],row[6],row[7],row[8])
                    #usuario = Usuario(row[0],row[1],row[2],row[3])
                    #usuario = Usuario(row[0])
                    usuarios.append(usuario.to_JSON())
            
            connection.close()
            return usuarios
        
        except Exception as ex:
            raise Exception(ex)
                