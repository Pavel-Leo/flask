from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField('email', validators=[Email()])
    password = PasswordField(
        'Пароль', validators=[DataRequired(), Length(min=8, max=100)]
    )

    remainme = BooleanField('Запомнить меня', default=False)
