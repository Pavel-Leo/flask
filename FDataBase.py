import math
import sqlite3
import time
from sqlite3 import Connection
from typing import List


class FDataBase:
    def __init__(self, db: Connection) -> None:
        self.__db = db
        self.__cur = db.cursor()

    def get_menu(self) -> List:
        sql = 'SELECT * FROM mainmenu'
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except Exception as ex:
            print(ex)
        return []

    def add_user(self, username: str, email: str, password: str) -> bool:
        try:
            self.__cur.execute(
                (
                    'SELECT COUNT() as "count" FROM users WHERE username = ?'
                    ' OR email = ?'
                ),
                (username, email),
            )
            res = self.__cur.fetchone()
            if res['count'] > 0:
                return False

            created_at = math.floor(time.time())
            self.__cur.execute(
                'INSERT INTO users VALUES (NULL, ?, ?, ?, ?)',
                (username, email, password, created_at),
            )
            self.__db.commit()
        except sqlite3.Error():
            return False
        return True

    def add_customer(self, username: str, phone: int) -> bool:
        try:
            created_at = math.floor(time.time())
            self.__cur.execute(
                'SELECT * FROM customers WHERE phone = ?',
                (phone,),
            )
            existing_customer = self.__cur.fetchone()
            if existing_customer is None:
                self.__cur.execute(
                    'INSERT INTO customers VALUES (NULL, ?, ?, ?)',
                    (username, phone, created_at),
                )
                self.__db.commit()
                return True
            else:
                return False
        except Exception as ex:
            print(ex)
            return False

    def get_customers(self) -> List:
        try:
            self.__cur.execute('SELECT * FROM customers')
            res = self.__cur.fetchall()
            if res:
                return res
        except Exception as ex:
            print(ex)
        return 'пусто'
