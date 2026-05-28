from __future__ import annotations

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=128)])
    remember = BooleanField("Recordarme")
    submit = SubmitField("Ingresar")


class CsvUploadForm(FlaskForm):
    csv_file = FileField(
        "Archivo CSV",
        validators=[FileRequired(), FileAllowed(["csv"], "Solo se permiten archivos CSV.")],
    )
    submit = SubmitField("Importar CSV")
