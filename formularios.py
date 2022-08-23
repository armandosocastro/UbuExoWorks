import email
#from msilib.schema import CheckBox
from flask_wtf import FlaskForm
import sqlalchemy
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, email_validator
from wtforms_sqlalchemy.fields import QuerySelectField
from models.Usuarios import Rol



class FormRegistro(FlaskForm):
    #username = StringField('Nombre de usuario', validators=[DataRequired()])
    empresa = StringField('Empresa', validators=[DataRequired()])
    cif = StringField('Cif', validators=[DataRequired()])
    planContratado = StringField('Plan', validators=[DataRequired()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField('Repita su contraseña', validators=[DataRequired(), EqualTo('password', 'Las contraseñas no coinciden')])

    submit = SubmitField('Registro') 
   
class FormLogin(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    rememberme = BooleanField('Recuerdame')
    
    submit = SubmitField('Login')

class FormCambioPassword(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    passwordActual = PasswordField('Contraseña actual', validators=[DataRequired()])
    password = PasswordField('Contraseña nueva', validators=[DataRequired()])
    password2 = PasswordField('Repita su contraseña', validators=[DataRequired(), EqualTo('password', 'Las contraseñas no coinciden')])
    
    submit = SubmitField('CambioPass')
    
    
#Obtenemos los Roles disponibles
def roles_opcion():
    roles = Rol.get_by_Rol()
    return Rol.get_by_Rol()

class FormAlta(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    nif = StringField('Nif', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    #Ponemos en una lista los roles disponibles sacandolos de la tabla ROL
    #rol = QuerySelectField(query_factory=lambda: roles_opcion(), get_label='idRol')
    rol = SelectField('Rol', choices=[])
    
    submit = SubmitField('Alta') 

class FormModifica(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    nif = StringField('Nif', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    #rol = QuerySelectField(query_factory=lambda: roles_opcion(), get_label='idRol')
    rol = SelectField('Rol', choices=[], coerce=int)
    estado = BooleanField('Habilitado')
    
    submit_modifica = SubmitField('Modifica') 
    submit_baja = SubmitField('Baja')

 
 
 
 
 
 

 