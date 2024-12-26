import pytest
import uuid
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book


class TestReceive:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.seller_id = f"test_receive_books_seller_id_{uuid.uuid1()}"
        self.store_id = f"test_receive_books_store_id_{uuid.uuid1()}"
        self.buyer_id = f"test_receive_books_buyer_id_{uuid.uuid1()}"
        self.password = self.buyer_id
        
        gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = gen_book.seller
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        
        self.buyer = register_new_buyer(self.buyer_id, self.password)

        self.total_price = sum(book.price * num for book, num in self.buy_book_info_list if book.price is not None)

        code = self.buyer.add_funds(self.total_price + 1000000)
        assert code == 200

        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        code = self.buyer.payment(self.order_id)
        assert code == 200
        yield

    def test_successful_book_receipt(self):
        assert self.seller.send_books(self.seller_id, self.order_id) == 200
        assert self.buyer.receive_books(self.buyer_id, self.order_id) == 200

    def test_order_error(self):
        assert self.seller.send_books(self.seller_id, self.order_id) == 200
        assert self.buyer.receive_books(self.buyer_id, self.order_id + 'x') != 200

    def test_authorization_error(self):
        assert self.seller.send_books(self.seller_id, self.order_id) == 200
        assert self.buyer.receive_books(self.buyer_id + 'x', self.order_id) != 200

    def test_books_not_sent(self):
        assert self.buyer.receive_books(self.buyer_id, self.order_id) != 200

    def test_books_repeat_receipt(self):
        assert self.seller.send_books(self.seller_id, self.order_id) == 200
        assert self.buyer.receive_books(self.buyer_id, self.order_id) == 200
        assert self.buyer.receive_books(self.buyer_id, self.order_id) != 200
