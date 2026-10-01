from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ServicioForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired()])
    precio = FloatField("Precio", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Guardar")
