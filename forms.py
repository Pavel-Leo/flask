import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, validators
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField('email', validators=[Email()])
    password = PasswordField(
        'Пароль', validators=[DataRequired(), Length(min=8, max=100)]
    )

    remainme = BooleanField('Запомнить меня', default=False)


def validate_username(form, field):
    username = field.data
    if not re.match(r'^[\wа-яА-Я]+$', username):
        raise ValidationError("Имя пользователя может содержать только буквы и цифры.")

class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), validate_username])
    email = StringField('email', validators=[Email()])
    password = PasswordField(
        'Пароль', validators=[DataRequired(), Length(min=8, max=100)]
    )
    password_again = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')]
    )




