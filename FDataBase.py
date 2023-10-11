import math
import sqlite3
import time


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def get_menu(self):
        sql = "SELECT * FROM mainmenu"
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except Exception as ex:
            print(ex)
        return []

    def add_user(self, username, email, password) -> bool:
        try:
            self.__cur.execute(
                f"SELECT COUNT() as 'count' FROM users WHERE username = ? OR email = ?", (username, email)
            )
            res = self.__cur.fetchone()
            if res['count'] > 0:
                return False

            created_at = math.floor(time.time())
            self.__cur.execute(
                "INSERT INTO users VALUES (NULL, ?, ?, ?, ?)",
                (username, email, password, created_at),
            )
            self.__db.commit()
        except sqlite3.Error() as ex:
            return False
        return True

    def add_customer(self, username, phone) -> bool:
        try:
            created_at = math.floor(time.time())
            self.__cur.execute(
                "SELECT * FROM customers WHERE phone = ?",
                (phone,),
            )
            existing_customer = self.__cur.fetchone()
            if existing_customer is None:
                self.__cur.execute(
                    "INSERT INTO customers VALUES (NULL, ?, ?, ?)",
                    (username, phone, created_at),
                )
                self.__db.commit()
                return True
            else:
                return False
        except Exception as ex:
            print(ex)
            return False

    def get_customers(self):
        try:
            self.__cur.execute("SELECT * FROM customers")
            res = self.__cur.fetchall()
            if res:
                return res
        except Exception as ex:
            print(ex)
        return 'пусто'
