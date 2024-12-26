import json
import pytest
import uuid
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.access.search import RequestSearch
from fe.access import book


class TestSearch:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.buyer_id = f"test_new_search_buyer_id_{uuid.uuid1()}"
        self.password = f"test_new_search_buyer_password_{uuid.uuid1()}"
        self.buyer = register_new_buyer(self.buyer_id, self.password)

        self.user_id = f"test_create_store_user_{uuid.uuid1()}"
        self.store_id = f"test_create_store_store_{uuid.uuid1()}"
        self.seller = register_new_seller(self.user_id, self.user_id)
        
        assert self.seller.create_store(self.store_id) == 200
        
        self.keyword = "hello"
        self.rs = RequestSearch()
        book_db = book.BookDB()
        self.book_example = book_db.get_book_info(0, 1)[0]

    def test_all_field_search(self):
        content, code = self.buyer.search(self.keyword)
        content = json.loads(content)['message']
        print(content, len(content))
        assert code == 200

    def test_pagination(self):
        content, code = self.buyer.search(self.keyword, page=2)
        assert code == 200

    def test_search_title(self):
        title = f"hello_{uuid.uuid1()}"
        self.book_example.title = title
        assert self.seller.add_book(self.store_id, 0, self.book_example) == 200

        assert self.rs.request_search_title(title=title) == 200
        assert self.rs.request_search_title(title=f"{title}x") == 501

    def test_search_title_in_store(self):
        title = f"hello_{uuid.uuid1()}"
        self.book_example.title = title
        self.seller.add_book(self.store_id, 0, self.book_example)

        assert self.rs.request_search_title_in_store(title=title, store_id=self.store_id) == 200
        assert self.rs.request_search_title_in_store(title=f"{title}x", store_id=self.store_id) == 501

    def test_search_tag(self):
        tag = f"hello_{uuid.uuid1()}"
        self.book_example.tags = [tag]
        self.seller.add_book(self.store_id, 0, self.book_example)

        assert self.rs.request_search_tag(tag=tag) == 200
        assert self.rs.request_search_tag(tag=f"{tag}x") == 501

    def test_search_tag_in_store(self):
        tag = f"hello_{uuid.uuid1()}"
        self.book_example.tags = [tag]
        self.seller.add_book(self.store_id, 0, self.book_example)

        assert self.rs.request_search_tag_in_store(tag=tag, store_id=self.store_id) == 200
        assert self.rs.request_search_tag_in_store(tag=f"{tag}x", store_id=self.store_id) == 501

    def test_search_author(self):
        author = f"hello_{uuid.uuid1()}"
        self.book_example.author = author
        self.seller.add_book(self.store_id, 0, self.book_example)

        assert self.rs.request_search_author(author=author) == 200
        assert self.rs.request_search_author(author=f"{author}x") == 501

    def test_search_author_in_store(self):
        author = f"hello_{uuid.uuid1()}"
        self.book_example.author = author
        self.seller.add_book(self.store_id, 0, self.book_example)

        assert self.rs.request_search_author_in_store(author=author, store_id=self.store_id) == 200
        assert self.rs.request_search_author_in_store(author=f"{author}x", store_id=self.store_id) == 501

    def test_search_content(self):
        key = "hello11"
        book_intro = f"{uuid.uuid1()} {key} {uuid.uuid1()}"
        self.book_example.book_intro = book_intro
        self.seller.add_book(self.store_id, 0, self.book_example)

        assert self.rs.request_search_content(content=key) == 200
        assert self.rs.request_search_content(content=f"{key}x") == 501

    def test_search_content_in_store(self):
        key = "hello12"
        book_intro = f"{uuid.uuid1()} {key} {uuid.uuid1()}"
        self.book_example.book_intro = book_intro
        self.seller.add_book(self.store_id, 0, self.book_example)

        assert self.rs.request_search_content_in_store(content=key, store_id=self.store_id) == 200
        assert self.rs.request_search_content_in_store(content=f"{key}x", store_id=self.store_id) == 501
