import json

from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.book import Book

bp_search = Blueprint("search", __name__, url_prefix="/search")


@bp_search.route("/title", methods=["GET"])
def search_title():
    return search_title_in_store()


@bp_search.route("/title_in_store", methods=["GET"])
def search_title_in_store():
    title = request.args.get("title")
    store_id = request.args.get("store_id")
    page_num = request.args.get("page_num")
    page_size = request.args.get("page_size")
    if title is None:
        title = ""
    if store_id is None:
        store_id = ""
    if page_num is None:
        page_num = 1
    if page_size is None:
        page_size = 10
    book = Book()
    code, message, books = book.search_title_in_store(title, store_id, page_num, page_size)
    # return jsonify({"data": books, "message": message, "code": code})
    return jsonify({"data": str(books), "message": message, "code": code})

@bp_search.route("/tag", methods=["GET"])
def search_tag():
    return search_tag_in_store()


@bp_search.route("/tag_in_store", methods=["GET"])
def search_tag_in_store():
    tag = request.args.get("tag")
    store_id = request.args.get("store_id")
    page_num = request.args.get("page_num")
    page_size = request.args.get("page_size")
    if tag is None:
        tag = ""
    if store_id is None:
        store_id = ""
    if page_num is None:
        page_num = 1
    if page_size is None:
        page_size = 10
    book = Book()
    code, message, books = book.search_tag_in_store(tag, store_id, page_num, page_size)
    return jsonify({"data": str(books), "message": message, "code": code})


@bp_search.route("/content", methods=["GET"])
def search_content():
    return search_content_in_store()


@bp_search.route("/content_in_store", methods=["GET"])
def search_content_in_store():
    content = request.args.get("content")
    store_id = request.args.get("store_id")
    page_num = request.args.get("page_num")
    page_size = request.args.get("page_size")
    if content is None:
        content = ""
    if store_id is None:
        store_id = ""
    if page_num is None:
        page_num = 1
    if page_size is None:
        page_size = 10
    book = Book()
    code, message, books = book.search_content_in_store(content, store_id, page_num, page_size)
    return jsonify({"data": str(books), "message": message, "code": code})


@bp_search.route("/author", methods=["GET"])
def search_author():
    return search_author_in_store()


@bp_search.route("/author_in_store", methods=["GET"])
def search_author_in_store():
    author = request.args.get("author")
    store_id = request.args.get("store_id")
    page_num = request.args.get("page_num")
    page_size = request.args.get("page_size")
    if author is None:
        author = ""
    if store_id is None:
        store_id = ""
    if page_num is None:
        page_num = 1
    if page_size is None:
        page_size = 10
    book = Book()
    code, message, books = book.search_author_in_store(author, store_id, page_num, page_size)
    return jsonify({"data": str(books), "message": message, "code": code})