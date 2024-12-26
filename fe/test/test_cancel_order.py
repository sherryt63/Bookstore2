import pytest

from fe.access.book import Book
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer

import uuid

class TestCancelOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):

        # 生成唯一的卖家ID、商店ID和买家ID
        self.seller_id = "test_cancel_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_cancel_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_cancel_order_buyer_id_{}".format(str(uuid.uuid1()))
        
        self.password = self.buyer_id     # 将买家的ID设为其密码

        gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = gen_book.seller

        # 生成书籍，设置非存在书籍ID和低库存水平的参数
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        
        # 获取购买书籍信息和ID列表
        self.buy_book_info_list = gen_book.buy_book_info_list
        self.buy_book_id_list = buy_book_id_list

        # 确保书籍生成成功
        assert ok

        # 注册新的买家
        self.buyer = register_new_buyer(self.buyer_id, self.password)

        # 计算购买书籍的总价格
        self.total_price = sum(item[0].price * item[1] for item in self.buy_book_info_list if item[0].price is not None)

        # 向买家账户添加资金（总价格 + 1000000）
        code = self.buyer.add_funds(self.total_price + 1000000)
        assert code == 200
        yield

    #测试已付款订单的取消
    def test_paid(self):
        code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code == 200

    #测试未付款订单的取消
    def test_unpaid(self):
        code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code == 200

    #测试已付款订单，使用无效 order_id 进行取消
    def test_invalid_order_id_paid(self):
        code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id, self.order_id + 'x')
        assert code != 200

    #测试未付款订单，使用无效 order_id 进行取消
    def test_invalid_order_id_unpaid(self):
        code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id, self.order_id + 'x')
        assert code != 200

    #测试买家 ID 错误情况下已付款订单的取消
    def test_authorization_error_paid(self):
        code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id + 'x', self.order_id)
        assert code != 200

    #测试买家 ID 错误情况下未付款订单的取消
    def test_authorization_error_unpaid(self):
        code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id + 'x', self.order_id)
        assert code != 200

    #测试重复取消已付款订单
    def test_repeat_cancel_paid(self):
        code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code != 200

    #测试重复取消未付款订单
    def test_repeat_cancel_not_paid(self):
        code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.buyer_id, self.order_id)
        assert code != 200