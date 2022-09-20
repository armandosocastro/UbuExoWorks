import email

from flask_wtf import FlaskForm
import sqlalchemy
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, email_validator, Regexp
from wtforms_sqlalchemy.fields import QuerySelectField
from models.Modelo import Rol



class FormRegistro(FlaskForm):

    empresa = StringField('Empresa', validators=[DataRequired()])
    cif = StringField('Cif', validators=[DataRequired()])
    planContratado = StringField('Plan', validators=[DataRequired()], default=1)
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    nif = StringField('Nif', validators=[Regexp('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][A-Z]', message="NIF incorrecto")])
    tlf = StringField('Telefono', validators=[Regexp('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', message="Campo obliogatorio")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    emailRecuperacion = StringField('Email recuperacion', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField('Repita su contraseña', validators=[DataRequired(), EqualTo('password', 'Las contraseñas no coinciden')])

    submit = SubmitField('Registro') 
   
class FormLogin(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    rememberme = BooleanField('Recuerdame')
    
    submit = SubmitField('Login')
    
class FormRecupera(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    submit = SubmitField('Recuperar')
    cancel = SubmitField('Cancelar', render_kw={'formnovalidate': True})


class FormCambioPassword(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    passwordActual = PasswordField('Contraseña actual', validators=[DataRequired()])
    password = PasswordField('Contraseña nueva', validators=[DataRequired()])
    password2 = PasswordField('Repita su contraseña', validators=[DataRequired(), EqualTo('password', 'Las contraseñas no coinciden')])
    
    submit = SubmitField('Cambiar contraseña')
    cancel = SubmitField('Cancelar', render_kw={'formnovalidate': True})
    
    
#Obtenemos los Roles disponibles
def roles_opcion():
    roles = Rol.get_by_Rol()
    return roles

class FormAlta(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message="Campo obliogatorio")])
    apellidos = StringField('Apellidos', validators=[DataRequired(message="Campo obliogatorio")])
    nif = StringField('Nif', validators=[Regexp('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][A-Z]', message="NIF incorrecto")])
    email = StringField('Email', validators=[DataRequired(message="Formato correo incorrecto"), Email()])
    emailRecuperacion = StringField('Email alternativo', validators=[DataRequired(message="Formato correo incorrecto"), Email()])
    tlf = StringField('Telefono', validators=[Regexp('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', message="Campo obliogatorio")])
    #Ponemos en una lista los roles disponibles sacandolos de la tabla ROL
    #rol = QuerySelectField(query_factory=lambda: roles_opcion(), get_label='idRol')
    rol = SelectField('Rol', choices=[])
    
    submit = SubmitField('Alta') 

class FormModifica(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message="Campo obligatorio")])
    apellidos = StringField('Apellidos', validators=[DataRequired(message="Campo obligatorio")])
    nif = StringField('Nif', validators=[Regexp('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][A-Z]', message="NIF incorrecto")])
    tlf = StringField('Telefono', validators=[Regexp('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', message="Campo obliogatorio")])
    email = StringField('Email', validators=[DataRequired(message="Formato correo incorrecto"), Email()])
    emailRecuperacion = StringField('Email alternativo', validators=[DataRequired(message="Formato correo incorrecto"), Email()])
    imei = StringField('Imei dispositivo registrado', render_kw={'readonly': True})

    rol = SelectField('Rol', choices=[], coerce=int)
    estado = BooleanField('Habilitado')
    
    submit_modifica = SubmitField('Modifica') 
    submit_baja = SubmitField('Baja')

 
 
 
 
 
 

 