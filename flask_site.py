import os
import re
import sqlite3
from sqlite3 import Connection
from typing import Literal, Tuple, Union

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.security import check_password_hash, generate_password_hash

from FDataBase import FDataBase
from flask import (
    Flask,
    Response,
    abort,
    flash,
    g,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from forms import LoginForm, RegisterForm
from UserLogin import UserLogin

DATABASE = '/tmp/flask_site.db'
DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY_DB')
MAX_CONTENT_LENGTH = 1024 * 1024
dbase = None

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flask_site.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите в систему'
login_manager.login_message_category = 'success'


@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().from_db(user_id, dbase)


def connect_db() -> Connection:
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db() -> None:
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db() -> Connection:
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.before_request
def before_request() -> None:
    """Подключение к БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error) -> None:
    """Закрытие соединения с БД"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


MENU: list[dict[str, str]] = [
    {'name': 'ГЛАВНАЯ', 'url': '/'},
    {'name': 'О НАС', 'url': 'about'},
    {'name': 'СЕРВИСЫ', 'url': 'services'},
    {'name': 'КОНТАКТЫ', 'url': 'contact'},
]


@app.errorhandler(404)
def page_not_found(error) -> Tuple[str, Literal[404]]:
    return (
        render_template('404.html', title='Страница не найдена', menu=MENU),
        404,
    )


@app.route('/', methods=['GET', 'POST'])
@login_required
def index() -> Union[Response, str]:
    if request.method == 'POST':
        name = request.form['username']
        phone = request.form['phone']
        response_data = {
            'status': 'error',
            'message': 'Ошибка при отправке формы',
        }

        if len(name) > 0 and name.isalpha() and len(phone) > 10:
            if (phone[:2] == '+7' and len(phone) == 12) or (
                phone[0] == '8' and len(phone) == 11
            ):
                res = dbase.add_customer(
                    request.form['username'],
                    request.form['phone'],
                )
                if res:
                    response_data = {
                        'status': 'success',
                        'message': (
                            'Сообщение отправлено. Наш специалист свяжется с'
                            ' вами в ближайшее время.'
                        ),
                    }
                else:
                    response_data['message'] = (
                        'Неверный формат номера телефона или вы уже заполняли'
                        ' форму'
                    )
        else:
            response_data['message'] = (
                'Не все поля заполнены верно. Поле "Имя" не может быть пустым'
                ' и должно содержать только буквы, формат телефона 8 или +7'
            )
        return jsonify(response_data)
    return render_template(
        'index.html',
        title='Главная страница',
        menu=dbase.get_menu(),
    )


@app.route('/personal')
def personal() -> Response:
    return render_template(
        'personal.html',
        title='Персональные данные',
        menu=dbase.get_menu(),
        pers=dbase.get_customers(),
    )


@app.route('/register', methods=['GET', 'POST'])
def register() -> Union[Response, str]:
    form = RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.password.data)
        res = dbase.add_user(
            form.username.data,
            form.email.data,
            hash,
        )
        if res:
            flash('Вы успешно зарегистрировались', category='success')
            return redirect(url_for('login'))
        else:
            flash(
                'Такой email или логин уже зарегистрирован, или пароли не совпадают',
                category='error',
            )
    return render_template(
        'register.html',
        menu=dbase.get_menu(),
        title='Регистрация',
        form=form,
    )


@app.route('/login', methods=['GET', 'POST'])
def login() -> Response:
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.get_user_by_email(form.email.data)
        if user and check_password_hash(user['password'], form.password.data):
            userlogin = UserLogin().create(user)
            remainme = form.remainme.data
            login_user(userlogin, remember=remainme)
            return redirect(request.args.get('next') or url_for('profile'))
        else:
            flash(
                'Неверный логин или пароль. Проверьте правильность',
                category='error',
            )

    return render_template(
        'login.html', menu=dbase.get_menu(), title='Авторизация', form=form,
    )
    # if request.method == 'POST':
    #     user = dbase.get_user_by_email(request.form['email'])
    #     if user and check_password_hash(
    #         user['password'],
    #         request.form['password'],
    #     ):
    #         userlogin = UserLogin().create(user)
    #         remainme = True if request.form.get('remainme') else False

    #         login_user(userlogin, remember=remainme)
    #         return redirect(request.args.get('next') or url_for('profile'))
    #     else:
    #         flash(
    #             'Неверный логин или пароль. Проверьте правильность',
    #             category='error',
    #         )
    # return render_template(
    #     'login.html',
    #     menu=dbase.get_menu(),
    #     title='Авторизация',
    # )


@app.route('/logout')
@login_required
def logout() -> Response:
    logout_user()
    flash('Вы вышли из профиля', category='success')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile() -> str:
    return render_template(
        'profile.html',
        menu=dbase.get_menu(),
        title='Профиль пользователя',
    )


@app.route('/user_avatar', methods=['GET', 'POST'])
@login_required
def user_avatar() -> str:
    img = current_user.get_avatar(app)
    if not img:
        return ""
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload() -> str:
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verify_ext(file.filename):
            try:
                img = file.read()
                res = dbase.update_avatar(img, current_user.get_id())
                if not res:
                    flash('Ошибка при обновлении аватара', category='error')
                flash('Аватар обновлен', category='success')
            except FileNotFoundError as e:
                flash('Ошибка при обновлении аватара', category='error')
        else:
            flash('Ошибка при обновлении аватара', category='error')

    return redirect(url_for('profile'))


@app.route('/about')
def about() -> str:
    return '<h1>About Page</h1>'


if __name__ == '__main__':
    app.run(debug=True)
