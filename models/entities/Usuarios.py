from tkinter.messagebox import NO


class Usuario():
    
    def __init__(self, idUsuario, nombre=None, apellidos=None, login=None, password=None, 
                 estado=None, idEmpresa=None,idJornadaLaboral=None, idRol=None) -> None:
        self.idUsuario=idUsuario
        self.nombre=nombre
        self.apellidos=apellidos
        self.login=login
        self.password=password
        self.estado=estado
        self.idEmpresa=idEmpresa
        self.idJornadaLaboral=idJornadaLaboral
        self.idRol=idRol
        
    def to_JSON(self):
        return {
            'idUsuario': self.idUsuario,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'login': self.login,
            'password': self.password,
            'estado': self.estado,
            'idEmpresa': self.idEmpresa,
            'idJornadaLaboral': self.idJornadaLaboral,
            'idRol': self.idRol
        }
        
