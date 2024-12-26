import uuid 
import json
import logging
from be.model import db_conn
from be.model import error
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            with self.conn.cursor() as cursor:
                # Begin transaction
                self.conn.begin()

                # Check if user exists
                cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = %s", (user_id,))
                if cursor.fetchone()[0] == 0:
                    return error.error_non_exist_user_id(user_id) + (order_id,)

                # Check if store exists
                cursor.execute("SELECT COUNT(*) FROM stores WHERE store_id = %s", (store_id,))
                if cursor.fetchone()[0] == 0:
                    return error.error_non_exist_store_id(store_id) + (order_id,)

                uid = f"{user_id}_{store_id}_{str(uuid.uuid1())}"
                total_price = 0

                for book_id, count in id_and_count:
                    # Check book stock level
                    cursor.execute(
                        "SELECT stock_level, price FROM books WHERE store_id = %s AND book_id = %s", 
                        (store_id, book_id)
                    )
                    result = cursor.fetchone()

                    if not result:
                        return error.error_non_exist_book_id(book_id) + (order_id,)

                    stock_level, price = result

                    if stock_level < count:
                        return error.error_stock_level_low(book_id) + (order_id,)

                    # Update stock level
                    cursor.execute(
                        "UPDATE books SET stock_level = stock_level - %s WHERE store_id = %s AND book_id = %s",
                        (count, store_id, book_id)
                    )

                    # Insert into order details
                    cursor.execute(
                        "INSERT INTO order_details (order_id, book_id, count, price) VALUES (%s, %s, %s, %s)",
                        (uid, book_id, count, price)
                    )

                    total_price += price * count

                # Insert into orders
                now_time = datetime.utcnow()
                cursor.execute(
                    "INSERT INTO orders (order_id, store_id, user_id, create_time, price, status) VALUES (%s, %s, %s, %s, %s, %s)",
                    (uid, store_id, user_id, now_time, total_price, 0)
                )

                order_id = uid
                self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            logging.error("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            with self.conn.cursor() as cursor:
                # Begin transaction
                self.conn.begin()

                # Check order status
                cursor.execute(
                    "SELECT user_id, store_id, price FROM orders WHERE order_id = %s AND status = 0",
                    (order_id,)
                )
                result = cursor.fetchone()
                if not result:
                    return error.error_invalid_order_id(order_id)

                buyer_id, store_id, total_price = result

                if buyer_id != user_id:
                    return error.error_authorization_fail()

                # Check user credentials
                cursor.execute(
                    "SELECT password, balance FROM users WHERE user_id = %s",
                    (buyer_id,)
                )
                result = cursor.fetchone()
                if not result or result[0] != password:
                    return error.error_authorization_fail()

                balance = result[1]

                if balance < total_price:
                    return error.error_not_sufficient_funds(order_id)

                # Deduct balance from buyer
                cursor.execute(
                    "UPDATE users SET balance = balance - %s WHERE user_id = %s",
                    (total_price, buyer_id)
                )

                # Add balance to seller
                cursor.execute(
                    "SELECT user_id FROM stores WHERE store_id = %s",
                    (store_id,)
                )
                result = cursor.fetchone()

                if not result:
                    return error.error_non_exist_store_id(store_id)

                seller_id = result[0]
                cursor.execute(
                    "UPDATE users SET balance = balance + %s WHERE user_id = %s",
                    (total_price, seller_id)
                )

                # Update order status
                cursor.execute(
                    "UPDATE orders SET status = 1 WHERE order_id = %s",
                    (order_id,)
                )

                self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            logging.error("528, {}".format(str(e)))
            return 528, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            with self.conn.cursor() as cursor:
                # Begin transaction
                self.conn.begin()

                # Check user credentials
                cursor.execute(
                    "SELECT password FROM users WHERE user_id = %s",
                    (user_id,)
                )
                result = cursor.fetchone()
                if not result or result[0] != password:
                    return error.error_authorization_fail()

                # Add funds
                cursor.execute(
                    "UPDATE users SET balance = balance + %s WHERE user_id = %s",
                    (add_value, user_id)
                )

                self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            logging.error("528, {}".format(str(e)))
            return 528, "{}".format(str(e))

        return 200, ""

    def receive_books(self, user_id: str, order_id: str) -> (int, str):
        try:
            with self.conn.cursor() as cursor:
                # Begin transaction
                self.conn.begin()

                # Check order status
                cursor.execute(
                    "SELECT user_id, status FROM orders WHERE order_id = %s",
                    (order_id,)
                )
                result = cursor.fetchone()

                if not result:
                    return error.error_invalid_order_id(order_id)

                buyer_id, paid_status = result

                if buyer_id != user_id:
                    return error.error_authorization_fail()

                if paid_status == 1:
                    return error.error_books_not_sent()

                if paid_status == 3:
                    return error.error_books_repeat_receive()

                # Update order status
                cursor.execute(
                    "UPDATE orders SET status = 3 WHERE order_id = %s",
                    (order_id,)
                )

                self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            logging.error("528, {}".format(str(e)))
            return 528, "{}".format(str(e))

        return 200, "ok"

    def cancel_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            with self.conn.cursor() as cursor:
                # Begin transaction
                self.conn.begin()

                # Check order status
                cursor.execute(
                    "SELECT user_id, store_id, price, status FROM orders WHERE order_id = %s",
                    (order_id,)
                )
                result = cursor.fetchone()

                if not result:
                    return error.error_invalid_order_id(order_id)

                buyer_id, store_id, price, status = result

                if buyer_id != user_id:
                    return error.error_authorization_fail()

                if status in [1, 2, 3]:
                    # Refund process
                    cursor.execute(
                        "SELECT user_id FROM stores WHERE store_id = %s",
                        (store_id,)
                    )
                    result = cursor.fetchone()

                    if not result:
                        return error.error_non_exist_store_id(store_id)

                    seller_id = result[0]

                    cursor.execute(
                        "UPDATE users SET balance = balance - %s WHERE user_id = %s",
                        (price, seller_id)
                    )

                    cursor.execute(
                        "UPDATE users SET balance = balance + %s WHERE user_id = %s",
                        (price, buyer_id)
                    )

                # Delete order
                cursor.execute(
                    "DELETE FROM orders WHERE order_id = %s",
                    (order_id,)
                )

                # Recover stock
                cursor.execute(
                    "SELECT book_id, count FROM order_details WHERE order_id = %s",
                    (order_id,)
                )
                for book_id, count in cursor.fetchall():
                    cursor.execute(
                        "UPDATE books SET stock_level = stock_level + %s WHERE store_id = %s AND book_id = %s",
                        (count, store_id, book_id)
                    )

                self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            logging.error("528, {}".format(str(e)))
            return 528, "{}".format(str(e))

        return 200, "ok"

    def check_hist_order(self, user_id: str):
        try:
            with self.conn.cursor() as cursor:
                # 未付款订单查询
                cursor.execute(
                    """
                    SELECT o.order_id, o.store_id, o.price, od.book_id, od.count, od.price
                    FROM orders o
                    JOIN order_details od ON o.order_id = od.order_id
                    WHERE o.user_id = %s AND o.status = 0
                    """, (user_id,)
                )
                unpaid_orders = cursor.fetchall()

                ans = []
                if unpaid_orders:
                    current_order_id = None
                    tmp_details = []
                    for record in unpaid_orders:
                        order_id, store_id, total_price, book_id, count, price = record
                        if current_order_id is None or current_order_id != order_id:
                            if current_order_id is not None:
                                ans.append({
                                    "status": "unpaid",
                                    "order_id": current_order_id,
                                    "buyer_id": user_id,
                                    "store_id": store_id,
                                    "total_price": total_price,
                                    "details": tmp_details
                                })
                            current_order_id = order_id
                            tmp_details = []
                        tmp_details.append({
                            "book_id": book_id,
                            "count": count,
                            "price": price
                        })
                    if current_order_id is not None:
                        ans.append({
                            "status": "unpaid",
                            "order_id": current_order_id,
                            "buyer_id": user_id,
                            "store_id": store_id,
                            "total_price": total_price,
                            "details": tmp_details
                        })

                # 已付款和取消订单查询
                cursor.execute(
                    """
                    SELECT o.order_id, o.store_id, o.price, o.status, od.book_id, od.count, od.price
                    FROM orders o
                    JOIN order_details od ON o.order_id = od.order_id
                    WHERE o.user_id = %s AND o.status IN (1, 2, 3, 4)
                    """, (user_id,)
                )
                paid_and_cancelled_orders = cursor.fetchall()

                if paid_and_cancelled_orders:
                    current_order_id = None
                    tmp_details = []
                    for record in paid_and_cancelled_orders:
                        order_id, store_id, total_price, status, book_id, count, price = record
                        if current_order_id is None or current_order_id != order_id:
                            if current_order_id is not None:
                                ans.append({
                                    "status": "paid" if status != 4 else "cancelled",
                                    "order_id": current_order_id,
                                    "buyer_id": user_id,
                                    "store_id": store_id,
                                    "total_price": total_price,
                                    "details": tmp_details
                                })
                            current_order_id = order_id
                            tmp_details = []
                        tmp_details.append({
                            "book_id": book_id,
                            "count": count,
                            "price": price
                        })
                    if current_order_id is not None:
                        ans.append({
                            "status": "paid" if status != 4 else "cancelled",
                            "order_id": current_order_id,
                            "buyer_id": user_id,
                            "store_id": store_id,
                            "total_price": total_price,
                            "details": tmp_details
                        })

            if not ans:
                return 200, "ok", "No orders found"
            return 200, "ok", ans

        except Exception as e:
            logging.error("528, {}".format(str(e)))
            return 528, "{}".format(str(e))

    def auto_cancel_order(self) -> (int, str):
        try:
            with self.conn.cursor() as cursor:
                # 查询需要取消的订单
                wait_time = 20
                interval = datetime.utcnow() - timedelta(seconds=wait_time)
                cursor.execute(
                    """
                    SELECT o.order_id, od.book_id, od.count, o.store_id
                    FROM orders o
                    JOIN order_details od ON o.order_id = od.order_id
                    WHERE o.create_time <= %s AND o.status = 0
                """, (interval,)
                )
                orders_to_cancel = cursor.fetchall()

                for record in orders_to_cancel:
                    order_id, book_id, count, store_id = record
                    # 恢复库存
                    cursor.execute(
                        """
                        UPDATE books
                        SET stock_level = stock_level + %s
                        WHERE store_id = %s AND book_id = %s
                        """, (count, store_id, book_id)
                    )

                    # 更新订单状态为取消
                    cursor.execute(
                        """
                        UPDATE orders
                        SET status = 4
                        WHERE create_time <= %s AND status = 0
                        """, (interval,)
                    )

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            logging.error("528, {}".format(str(e)))
            return 528, "{}".format(str(e))

        return 200, "ok"


scheduler = BackgroundScheduler()
scheduler.add_job(Buyer().auto_cancel_order, 'interval', id='5_second_job', seconds=5)
scheduler.start()

