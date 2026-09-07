from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired

class FacturacionForm(FlaskForm):
    cliente = StringField("Cliente", validators=[DataRequired()])
    total = DecimalField("Total", validators=[DataRequired()])
    submit = SubmitField("Guardar")
