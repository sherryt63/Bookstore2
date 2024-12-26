import jwt
import time
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from be.model import error
from be.model import db_conn

def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")

def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded

class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 seconds

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = f"terminal_{str(time.time())}"
            token = jwt_encode(user_id, terminal)
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (user_id, password, balance, token, terminal)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (user_id, password, 0, token, terminal),
                )
            self.conn.commit()
        except psycopg2.IntegrityError:
            self.conn.rollback()
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT token FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                if result is None or not self.__check_token(user_id, result['token'], token):
                    return error.error_authorization_fail()
        except Exception as e:
            logging.error(str(e))
            return 528, "Internal error"
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT password FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                if result is None or result['password'] != password:
                    return error.error_authorization_fail()
        except Exception as e:
            logging.error(str(e))
            return 528, "Internal error"
        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE users
                    SET token = %s, terminal = %s
                    WHERE user_id = %s
                    """,
                    (token, terminal, user_id),
                )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logging.error(str(e))
            return 528, f"{str(e)}", ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> (int, str):
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = f"terminal_{str(time.time())}"
            dummy_token = jwt_encode(user_id, terminal)
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE users
                    SET token = %s, terminal = %s
                    WHERE user_id = %s
                    """,
                    (dummy_token, terminal, user_id),
                )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logging.error(str(e))
            return 528, f"{str(e)}"
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE user_id = %s AND password = %s", (user_id, password))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logging.error(str(e))
            return 530, f"{str(e)}"
        return 200, "ok"
