from flask_login import UserMixin

class UserLogin(UserMixin):
    """Авторизация пользователей"""

    def from_db(self, user_id, db):
        self.__user = db.get_user(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self) -> str:
        return str(self.__user['id'])
