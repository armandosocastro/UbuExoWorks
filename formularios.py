import email
#from msilib.schema import CheckBox
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, email_validator


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

class FormAlta(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    nif = StringField('Nif', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    submit = SubmitField('Alta') 

class FormModifica(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    nif = StringField('Nif', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    estado = BooleanField('Habilitado')
    
    submit_modifica = SubmitField('Modifica') 
    submit_baja = SubmitField('Baja')

 
 
 
 
 
 

 