

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, ForeignKey, DateTime, Integer, Text, Float, Time
from sqlalchemy.orm import relationship
from database.database import db
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(db.Model):
    
    __tablename__ = 'USUARIO'
    
    idUsuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45), nullable=False)
    apellidos = db.Column(db.String(45), nullable=False)
    login = db.Column(db.String(45), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    estado = db.Column(db.Boolean, nullable=False)
    idEmpresa = db.Column(db.Integer, ForeignKey('EMPRESA.idEmpresa'))
    empresa = db.relationship('Empresa')
    idJornadaLaboral = db.Column(db.Integer, ForeignKey('JORNADA_LABORAL.idJornadaLAboral'))
    jornada = db.relationship('Jornada_Laboral')                                
    idRol = db.Column(db.Integer, nullable=False)
    
    def __init__(self, idUsuario, nombre=None, apellidos=None, login=None, password=None, 
        estado=None, idEmpresa=None,idJornadaLaboral=None, idRol=None) -> None:
        self.idUsuario=idUsuario
        self.nombre=nombre
        self.apellidos=apellidos
        self.login=login
        self.password=generate_password_hash(password)
        self.estado=estado
        self.idEmpresa=idEmpresa
        self.idJornadaLaboral=idJornadaLaboral
        self.idRol=idRol
        
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
        
    @staticmethod
    def get_by_login(login):    
        return Usuario.query.filter_by(login=login).first()
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    #Metodo para poder serializarlo y enviarlo como un JSON
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
        
class Empresa(db.Model):
    
    __tablename__ = 'EMPRESA'
    
    idEmpresa = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45), nullable=False)
    cif = db.Column(db.String(20), nullable=False)
    planContratado = db.Column(db.Integer, nullable=False)
    
    def __init__(self, idEmpresa, nombre=None, cif=None, planContratado=None) -> None:
        self.idEmpresa = idEmpresa
        self.nombre = nombre
        self.cif = cif
        self.planContratado = planContratado
    
                 
    @staticmethod
    def get_by_id(idEmpresa):    
        return Empresa.query.filter_by(idEmpresa=idEmpresa).first()

    def to_JSON(self):
        return {
            'idEmpresa': self.idEmpresa,
            'nombre': self.nombre,
            'cif': self.cif,
            'planContratado': self.planContratado
        }  
    
class Jornada_Laboral(db.Model):
        
        __tablename__ = 'JORNADA_LABORAL'
    
        idJornadaLAboral = db.Column(db.Integer, primary_key=True)
        horaEntrada = db.Column(db.Time, nullable=False)
        horaSalida = db.Column(db.Time, nullable=False)
        horaEntrada2 = db.Column(db.Time, nullable=False)
        horaSalida2 = db.Column(db.Time, nullable=False)
        margenFichaje = db.Column(db.Time, nullable=False)
        horasJornada = db.Column(db.Time, nullable=False)
        idEmpresa = db.Column(db.Integer, ForeignKey('EMPRESA.idEmpresa'))
        empresa = db.relationship('Empresa')
                    
        def __init__(self, idJornadaLAboral, horaEntrada=None, horaSalida=None, horaEntrada2=None,
                    horaSalida2=None, margenFichaje=None, horasJornada=None, idEmpresa=None) -> None:
        
            self.idJornadaLAboral=idJornadaLAboral
            self.horaEntrada=horaEntrada
            self.horaSalida=horaSalida
            self.horaEntrada2=horaEntrada2
            self.horaSalida2=horaSalida2
            self.margenFichaje=margenFichaje
            self.horasJornada=horasJornada
            self.idEmpresa=idEmpresa

        @staticmethod
        def get_by_id(idJornadaLAboral):    
            return Jornada_Laboral.query.filter_by(idJornadaLAboral=idJornadaLAboral).first()
    
        def to_JSON(self):
            return {
                'idJornadaLAboral': self.idJornadaLAboral,
                'horaEntrada': self.horaEntrada,
                'horaSalida': self.horaSalida,
                'horaEntrada2': self.horaEntrada2,
                'horaSalida2': self.horaSalida2,
                'margenFichaje': self.margenFichaje,
                'horasJornada': self.horasJornada,
                'idEmpresa': self.idEmpresa
            }  