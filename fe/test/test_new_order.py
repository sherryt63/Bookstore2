import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid


class TestNewOrder:
    @pytest.fixture(autouse=True)
    #在每个测试用例运行前自动执行，用于初始化测试环境
    def pre_run_initialization(self):
        #生成唯一的买家 ID、卖家 ID 和商店 ID，确保测试数据独立性
        self.seller_id = "test_new_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_new_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id  
        self.buyer = register_new_buyer(self.buyer_id, self.password)     #注册一个新的买家
        self.gen_book = GenBook(self.seller_id, self.store_id)            #用于生成书籍数据
        yield

    def test_non_exist_book_id(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=True, low_stock_level=False
        )
        assert ok
        code, _ = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code != 200

    #测试库存不足
    def test_low_stock_level(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=True
        )
        assert ok
        code, _ = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code != 200

    #测试正常情况
    def test_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, _ = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

    def test_non_exist_user_id(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        self.buyer.user_id = self.buyer.user_id + "_x"
        code, _ = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code != 200

    def test_non_exist_store_id(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, _ = self.buyer.new_order(self.store_id + "_x", buy_book_id_list)
        assert code != 200
