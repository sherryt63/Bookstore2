import json
from be.model import error
from be.model import db_conn
from psycopg2 import sql, extras


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
            self,
            user_id: str,
            store_id: str,
            book_id: str,
            book_json_str: str,
            stock_level: int,
    ):
        try:
            with self.conn.cursor() as cursor:
                self.conn.autocommit = False

                if not self.user_id_exist(user_id):
                    return error.error_non_exist_user_id(user_id)
                if not self.store_id_exist(store_id):
                    return error.error_non_exist_store_id(store_id)
                if self.book_id_exist(store_id, book_id):
                    return error.error_exist_book_id(book_id)

                cursor.execute(
                    sql.SQL("""
                        INSERT INTO books (store_id, book_id, stock_level)
                        VALUES (%s, %s, %s)
                    """),
                    (store_id, book_id, stock_level)
                )

                book_details = json.loads(book_json_str)
                cursor.execute(
                    sql.SQL("""
                        INSERT INTO books (book_id, title, author, price, details)
                        VALUES (%s, %s, %s, %s, %s)
                    """),
                    (
                        book_id,
                        book_details.get("title"),
                        book_details.get("author"),
                        book_details.get("price"),
                        json.dumps(book_details)
                    )
                )

                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            with self.conn.cursor() as cursor:
                self.conn.autocommit = False

                if not self.user_id_exist(user_id):
                    return error.error_non_exist_user_id(user_id)
                if not self.store_id_exist(store_id):
                    return error.error_non_exist_store_id(store_id)
                if not self.book_id_exist(store_id, book_id):
                    return error.error_non_exist_book_id(book_id)

                cursor.execute(
                    sql.SQL("""
                        UPDATE books
                        SET stock_level = stock_level + %s
                        WHERE store_id = %s AND book_id = %s
                    """),
                    (add_stock_level, store_id, book_id)
                )

                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            with self.conn.cursor() as cursor:
                self.conn.autocommit = False

                if not self.user_id_exist(user_id):
                    return error.error_non_exist_user_id(user_id)
                if self.store_id_exist(store_id):
                    return error.error_exist_store_id(store_id)

                cursor.execute(
                    sql.SQL("""
                        INSERT INTO stores (store_id, user_id)
                        VALUES (%s, %s)
                    """),
                    (store_id, user_id)
                )

                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        return 200, "ok"

    def send_books(self, user_id: str, order_id: str) -> (int, str):
        try:
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cursor:
                self.conn.autocommit = False

                cursor.execute(
                    sql.SQL("""
                        SELECT * FROM orders
                        WHERE order_id = %s AND status IN (1, 2, 3)
                    """),
                    (order_id,)
                )
                result = cursor.fetchone()

                if result is None:
                    return error.error_invalid_order_id(order_id)

                store_id = result["store_id"]
                paid_status = result["status"]

                cursor.execute(
                    sql.SQL("""
                        SELECT user_id FROM stores WHERE store_id = %s
                    """),
                    (store_id,)
                )
                seller_result = cursor.fetchone()

                if seller_result["user_id"] != user_id:
                    return error.error_authorization_fail()
                if paid_status in (2, 3):
                    return error.error_books_repeat_sent()

                cursor.execute(
                    sql.SQL("""
                        UPDATE orders
                        SET status = 2
                        WHERE order_id = %s
                    """),
                    (order_id,)
                )

                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        return 200, "ok"
