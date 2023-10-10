import os
import sqlite3

from FDataBase import FDataBase
from flask import (
    Flask,
    abort,
    flash,
    g,
    get_flashed_messages,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

DATABASE = '/tmp/flask_site.db'
DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY_DB')
dbase = None

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flask_site.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db() -> None:
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
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
def page_not_found(error):
    return (
        render_template('404.html', title='Страница не найдена', menu=MENU),
        404,
    )


@app.route('/', methods=['GET', 'POST'])
def index():
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
                    request.form['username'], request.form['phone']
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
                        'Неверный формат номера телефона или вы уже заполняли форму'
                    )
        else:
            response_data['message'] = (
                'Не все поля заполнены верно. Поле "Имя" не может быть пустым'
                ' и должно содержать только буквы, формат телефона 8 или +7'
            )
        return jsonify(response_data)
    return render_template(
        'index.html', title='Главная страница', menu=dbase.get_menu()
    )


@app.route('/personal')
def personal():
    return render_template(
        'personal.html', title='Персональные данные', menu=dbase.get_menu(), pers=dbase.get_customers(),
    )


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         name = request.form['username']
#         phone = request.form['phone']
#         if len(name) > 0 and name.isalpha() and len(phone) > 10:
#             if (phone[:2] == '+7' and len(phone) == 12) or (
#                 phone[0] == '8' and len(phone) == 11
#             ):
#                 flash(
#                     (
#                         'Сообщение отправлено. Наш специалист свяжется с вами'
#                         ' в ближайшее время.'
#                     ),
#                     category='success',
#                 )
#             else:
#                 flash('Неверный формат номера телефона', category='error')
#         else:
#             flash(
#                 (
#                     'Не все поля заполнены верно. Поле "Имя" не может быть'
#                     ' пустым и должно содержать только буквы, формат телефона'
#                     ' 8 или +7'
#                 ),
#                 category='error',
#             )
#         for k, v in request.form.items():
#             print(v, end=', ')
#     print(url_for('index'))
#     return render_template('index.html', title='Главная страница', menu=MENU)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif (
        request.method == 'POST'
        and request.form['username'] == 'admin'
        and request.form['password'] == '123'
    ):
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html', title='Авторизация', menu=MENU)


@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Пользователь {username}'


@app.route('/about')
def about():
    return '<h1>About Page</h1>'


if __name__ == '__main__':
    app.run(debug=True)
