
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired


class PasswordForm(FlaskForm):

    password = PasswordField(
        "Contraseña",
        validators=[DataRequired()]
    )

    submit = SubmitField("Confirmar")

