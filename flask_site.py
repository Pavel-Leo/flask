import os

from flask import (
    Flask,
    flash,
    get_flashed_messages,
    render_template,
    request,
    url_for,
    jsonify
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

MENU: list[dict[str, str]] = [
    {'name': 'ГЛАВНАЯ', 'url': '/'},
    {'name': 'О НАС', 'url': 'about'},
    {'name': 'СЕРВИСЫ', 'url': 'services'},
    {'name': 'КОНТАКТЫ', 'url': 'contact'},
]


# from flask import jsonify

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['username']
        phone = request.form['phone']
        response_data = {'status': 'error', 'message': 'Ошибка при отправке формы'}

        if len(name) > 0 and name.isalpha() and len(phone) > 10:
            if (phone[:2] == '+7' and len(phone) == 12) or (
                phone[0] == '8' and len(phone) == 11
            ):
                response_data = {
                    'status': 'success',
                    'message': 'Сообщение отправлено. Наш специалист свяжется с вами в ближайшее время.',
                }
            else:
                response_data['message'] = 'Неверный формат номера телефона'
        else:
            response_data['message'] = (
                'Не все поля заполнены верно. Поле "Имя" не может быть пустым и должно содержать только буквы, формат телефона 8 или +7'
            )

        return jsonify(response_data)

    return render_template('index.html', title='Главная страница', menu=MENU)

@app.route('/profile/<int:username>')
def profile(username):
    return f'Пользователь {username}'


@app.route('/about')
def about():
    return '<h1>About Page</h1>'


if __name__ == '__main__':
    app.run(debug=True)
