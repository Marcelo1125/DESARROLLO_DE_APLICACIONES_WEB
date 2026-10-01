
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class ProductoForm(FlaskForm):

    nombre = StringField(
        "Nombre",
        validators=[DataRequired()]
    )

    precio = DecimalField(
        "Precio",
        validators=[DataRequired()]
    )

    stock = IntegerField(
        "Stock inicial",
        validators=[
            DataRequired(),
            NumberRange(min=0)
        ],
        default=0
    )

    submit = SubmitField("Guardar")

