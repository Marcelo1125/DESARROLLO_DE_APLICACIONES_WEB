from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class FacturacionForm(FlaskForm):
    estudiante_id = SelectField("Estudiante", coerce=int, validators=[DataRequired()])
    producto_id = SelectField("Producto", coerce=int, validators=[Optional()])
    servicio_id = SelectField("Servicio", coerce=int, validators=[Optional()])
    cantidad = IntegerField("Cantidad", validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField("Generar Factura")
