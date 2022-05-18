import email
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, email_validator

class FormRegistro(FlaskForm):
    #username = StringField('Nombre de usuario', validators=[DataRequired()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField('Repita su contraseña', validators=[DataRequired(), EqualTo('password', 'Las contraseñas no coinciden')])

    submit = SubmitField('Registro') 
       