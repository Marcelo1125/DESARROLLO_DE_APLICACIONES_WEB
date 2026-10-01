from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class ProveedorForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    empresa = StringField("Empresa", validators=[DataRequired()])
    telefono = StringField("Teléfono", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Guardar")