from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class ProveedorForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    telefono = StringField("Teléfono", validators=[DataRequired()])
    submit = SubmitField("Guardar")
