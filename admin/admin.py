import sqlite3
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

admin = Blueprint(
    'admin', __name__, template_folder='templates', static_folder='static'
)
menu = [
    {'url': '.index', 'title': 'Панель'},
    {'url': '.customers', 'title': 'Покупатели'},
    {'url': '.logout', 'title': 'Выход'},

]

db = None


@admin.before_request
def before_request():
    """Подключение к БД перед выполнением запроса"""
    global db
    db = g.get('link_db')


@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request


def login_admin():
    session['admin_logged'] = 1


def is_logged():
    return True if session.get('admin_logged') else False


def logout_admin():
    session.pop('admin_logged', None)

@admin.route('/')
def index():
    if not is_logged():
        return redirect(url_for('.login'))
    return render_template(
        'admin/index.html',
        menu=menu,
        title='Админ-панель',
    )


@admin.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged():
        return redirect(url_for('.index'))
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash(
                'Неверный логин или пароль. Проверьте правильность',
                category='error',
            )
    return render_template(
        'admin/login.html', title='Админ-панель',
    )


@admin.route('/logout', methods=['GET', 'POST'])
def logout():
    if not is_logged():
        return redirect(url_for('.login'))
    logout_admin()
    flash('Вы вышли из профиля', category='success')
    return redirect(url_for('.login'))


@admin.route('/customers')
def customers():
    if not is_logged():
        return redirect(url_for('.login'))

    list = []
    try:
        cur = db.cursor()
        cur.execute('SELECT id, username, phone FROM customers')
        list = cur.fetchall()
        print(list)
    except sqlite3.Error as ex:
        print('Error ' + str(ex))
    return render_template(
        'admin/customers.html', title='Список покупателей', menu=menu, list=list,
    )
