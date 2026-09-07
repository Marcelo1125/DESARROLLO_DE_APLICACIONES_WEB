from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired

class ProductoForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    precio = DecimalField("Precio", validators=[DataRequired()])
    submit = SubmitField("Guardar")
