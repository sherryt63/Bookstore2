from be.model import store

class DBConn:
    def __init__(self):
        # 获取数据库连接
        self.conn = store.get_db_conn().conn

    def user_id_exist(self, user_id):
        # 检查用户 ID 是否存在
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                SELECT 1 FROM users WHERE user_id = %s;
                """, (user_id,))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            self.conn.rollback()
            raise e

    def book_id_exist(self, store_id, book_id):
        # 检查书籍 ID 是否存在于某个商店
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                SELECT 1 FROM books b
                JOIN stores s ON s.store_id = %s
                WHERE b.book_id = %s;
                """, (store_id, book_id))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            self.conn.rollback()
            raise e

    def store_id_exist(self, store_id):
        # 检查商店 ID 是否存在
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                SELECT 1 FROM stores WHERE store_id = %s;
                """, (store_id,))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            self.conn.rollback()
            raise e
