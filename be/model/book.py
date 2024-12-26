from be.model import db_conn


class Book(db_conn.DBConn):

    def __init__(self):
        super().__init__()

    def _search_in_store(self, condition, store_id, page_num, page_size):
        # condition is a dictionary of conditions for querying
        with self.conn.cursor() as cursor:
            # Build the WHERE clause dynamically based on the condition
            where_clause = " AND ".join([f"{key} = %s" for key in condition.keys()])
            params = list(condition.values())

            query = f"""
                SELECT * FROM books
                WHERE {where_clause}
                LIMIT %s OFFSET %s
            """
            # Pagination parameters
            params.append(page_size)
            params.append((page_num - 1) * page_size)

            cursor.execute(query, tuple(params))
            result_list = cursor.fetchall()

            if store_id:
                result_list = self._filter_books_in_store(result_list, store_id)

            if not result_list:
                return 501, f"Books not found", []
            return 200, "ok", result_list

    def _filter_books_in_store(self, result_list, store_id):
        filtered_books = []
        with self.conn.cursor() as cursor:
            for book in result_list:
                book_id = book['book_id']
                cursor.execute("""
                    SELECT 1 FROM stores
                    WHERE store_id = %s AND EXISTS (
                        SELECT 1 FROM books WHERE book_id = %s
                    )
                """, (store_id, book_id))
                if cursor.fetchone():
                    filtered_books.append(book)
        return filtered_books

    def search_title_in_store(self, title: str, store_id: str, page_num: int, page_size: int):
        condition = {"title": title}
        return self._search_in_store(condition, store_id, page_num, page_size)

    def search_title(self, title: str, page_num: int, page_size: int):
        return self.search_title_in_store(title, "", page_num, page_size)

    def search_tag_in_store(self, tag: str, store_id: str, page_num: int, page_size: int):
        condition = {"tags": tag}  # Assuming 'tags' is a TEXT column
        return self._search_in_store(condition, store_id, page_num, page_size)

    def search_tag(self, tag: str, page_num: int, page_size: int):
        return self.search_tag_in_store(tag, "", page_num, page_size)

    def search_content_in_store(self, content: str, store_id: str, page_num: int, page_size: int):
        condition = {"content": content}  # Assuming 'content' is a TEXT column
        return self._search_in_store(condition, store_id, page_num, page_size)

    def search_content(self, content: str, page_num: int, page_size: int):
        return self.search_content_in_store(content, "", page_num, page_size)

    def search_author_in_store(self, author: str, store_id: str, page_num: int, page_size: int):
        condition = {"author": author}  # Assuming 'author' is a column in books table
        return self._search_in_store(condition, store_id, page_num, page_size)

    def search_author(self, author: str, page_num: int, page_size: int):
        return self.search_author_in_store(author, "", page_num, page_size)
