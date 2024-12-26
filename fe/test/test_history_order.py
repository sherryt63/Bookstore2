import pytest

from fe.access.book import Book
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer

import uuid

import random

class TestHistoryOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_check_hist_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id

        self.buyer = register_new_buyer(self.buyer_id, self.password)
        yield

    #验证在买家拥有订单记录时能正确返回历史订单信息
    def test_have_orders(self):
        for i in range(10):
            self.seller_id = "test_check_hist_order_seller_id_{}".format(str(uuid.uuid1()))
            self.store_id = "test_check_hist_order_store_id_{}".format(str(uuid.uuid1()))
            gen_book = GenBook(self.seller_id, self.store_id)
            self.seller = gen_book.seller

            ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
            self.buy_book_info_list = gen_book.buy_book_info_list
            assert ok

            self.total_price = sum(book.price * num for book, num in self.buy_book_info_list if book.price is not None)

            code = self.buyer.add_funds(self.total_price + 1000000)
            assert code == 200

            code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
            assert code == 200

            if random.choice([True, False]):   # 随机决定是否取消订单
                code = self.buyer.cancel_order(self.buyer_id, self.order_id)
                assert code == 200
                continue
            else:
                if random.choice([True, False]):  # 随机决定是否付款
                    code = self.buyer.payment(self.order_id)
                    assert code == 200
                    
                    # 发货和收货前
                    if random.choice([True, False]):  # 随机决定在发货前是否取消订单
                        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
                        assert code == 200
                        continue
                    else:
                        code = self.seller.send_books(self.seller_id, self.order_id)
                        assert code == 200
                        
                        # 发货后收货前
                        if random.choice([True, False]):  # 随机决定在收货前是否取消订单
                            code = self.buyer.cancel_order(self.buyer_id, self.order_id)
                            assert code == 200
                            continue
                        else:
                            code = self.buyer.receive_books(self.buyer_id, self.order_id)
                            assert code == 200
        code = self.buyer.check_hist_order(self.buyer_id)
        assert code == 200

    #验证查询不存在的用户ID时返回错误
    def test_non_exist_user_id(self):
        code = self.buyer.check_hist_order(self.buyer_id + 'x')
        assert code != 200

    #验证在没有订单记录的情况下能正确返回结果
    def test_no_orders(self):
        code = self.buyer.check_hist_order(self.buyer_id)
        assert code == 200
