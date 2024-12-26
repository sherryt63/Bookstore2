import psycopg2
from psycopg2.extras import DictCursor

class Store:
    def __init__(self, db_url):
        # 解析 db_url，连接到 PostgreSQL中的bookstore数据库
        self.conn = psycopg2.connect(db_url)
        self.init_tables()

    def init_tables(self):
        # 初始化 PostgreSQL 中的表
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(255) PRIMARY KEY,
                    password VARCHAR(255) NOT NULL,
                    balance NUMERIC DEFAULT 0,
                    token VARCHAR(512),
                    terminal VARCHAR(255)
                );
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS stores (
                    store_id VARCHAR(255) PRIMARY KEY,
                    store_name VARCHAR(255) UNIQUE NOT NULL,
                    user_id VARCHAR(255) REFERENCES users(user_id)   
                );
                """)

                #新添加stock_level和price和details
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    book_id SERIAL PRIMARY KEY,
                    store_id VARCHAR(255) REFERENCES stores(store_id),
                    title VARCHAR(255),
                    tags TEXT,
                    book_intro TEXT,
                    content TEXT,
                    author VARCHAR(255),
                    stock_level INT DEFAULT 0 CHECK (stock_level >= 0),
                    price NUMERIC NOT NULL,
                    details JSONB
                );
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id SERIAL PRIMARY KEY,
                    store_id VARCHAR(255) REFERENCES stores(store_id),
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    book_id INT REFERENCES books(book_id),
                    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    price NUMERIC NOT NULL,
                    status INT DEFAULT 0
                );
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_details (
                    order_detail_id SERIAL PRIMARY KEY,
                    order_id INT REFERENCES orders(order_id),
                    book_id INT REFERENCES books(book_id),
                    count INT NOT NULL,
                    price NUMERIC NOT NULL
                );
                """)

                

                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def insert_user(self, username, password):
        # 插入用户数据
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                INSERT INTO users (username, password)
                VALUES (%s, %s)
                RETURNING user_id;
                """, (username, password))
                self.conn.commit()
                return cursor.fetchone()[0]
        except Exception as e:
            self.conn.rollback()
            raise e

    def insert_store(self, store_name):
        # 插入店铺数据
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                INSERT INTO stores (store_name)
                VALUES (%s)
                RETURNING store_id;
                """, (store_name,))
                self.conn.commit()
                return cursor.fetchone()[0]
        except Exception as e:
            self.conn.rollback()
            raise e

    def insert_book(self, title, tags, book_intro, content):
        # 插入图书数据
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                INSERT INTO books (title, tags, book_intro, content)
                VALUES (%s, %s, %s, %s)
                RETURNING book_id;
                """, (title, tags, book_intro, content))
                self.conn.commit()
                return cursor.fetchone()[0]
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_user_by_id(self, user_id):
        # 查询用户数据
        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                SELECT * FROM users WHERE user_id = %s;
                """, (user_id,))
                return cursor.fetchone()
        except Exception as e:
            raise e

    def close(self):
        # 关闭数据库连接
        self.conn.close()


# 初始化数据库连接
def init_database(db_url):
    global database_instance
    database_instance = Store(db_url)

def get_db_conn():
    global database_instance
    db_url = "postgresql://Sherrytxy:newpassword@localhost:5432/bookstore"    #改成PostgreSQL数据库
    database_instance = Store(db_url)
    return database_instance
