import requests
import json

class RequestSearch:
    def __init__(self):
        self.url_prefix = "http://127.0.0.1:5000/search"

    def request_search_title(self, title):
        params = {
            "title": title
        }
        # print(simplejson.dumps(json))
        url = self.url_prefix + "/title"
        # headers = {"token": self.token}
        r = requests.get(url,params=params)
        res = json.loads(r.text)
        return res['code']

    def request_search_title_in_store(self, title, store_id):
        params = {
            "title": title,
            "store_id": store_id
        }
        # print(simplejson.dumps(json))
        url = self.url_prefix + "/title_in_store"
        # headers = {"token": self.token}
        r = requests.get(url,params=params)
        res = json.loads(r.text)
        return res['code']

    def request_search_tag(self, tag):
        params = {
            "tag": tag
        }
        # print(simplejson.dumps(json))
        url = self.url_prefix + "/tag"
        # headers = {"token": self.token}
        r = requests.get(url, params=params)
        res = json.loads(r.text)
        return res['code']

    def request_search_tag_in_store(self, tag, store_id):
        params = {
            "tag": tag,
            "store_id": store_id
        }
        # print(simplejson.dumps(json))
        url = self.url_prefix + "/tag_in_store"
        # headers = {"token": self.token}
        r = requests.get(url, params=params)
        res = json.loads(r.text)
        return res['code']

    def request_search_author(self, author):
        params = {
            "author": author
        }
        # print(simplejson.dumps(json))
        url = self.url_prefix + "/author"
        # headers = {"token": self.token}
        r = requests.get(url, params=params)
        res = json.loads(r.text)
        return res['code']

    def request_search_author_in_store(self, author, store_id):
        params = {
            "author": author,
            "store_id": store_id
        }
        # print(simplejson.dumps(json))
        url = self.url_prefix + "/author_in_store"
        # headers = {"token": self.token}
        r = requests.get(url, params=params)
        res = json.loads(r.text)
        return res['code']

    def request_search_content(self, content):
        params = {
            "content": content
        }
        # print(simplejson.dumps(json))
        url = self.url_prefix + "/content"
        # headers = {"token": self.token}
        r = requests.get(url, params=params)
        res = json.loads(r.text)
        return res['code']

    def request_search_content_in_store(self, content, store_id):
        params = {
            "content": content,
            "store_id": store_id
        }
        # print(simplejson.dumps(json))
        url = self.url_prefix + "/content_in_store"
        # headers = {"token": self.token}
        r = requests.get(url, params=params)
        res = json.loads(r.text)
        return res['code']
