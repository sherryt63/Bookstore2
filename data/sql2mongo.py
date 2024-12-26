import sqlite3
from pymongo import MongoClient
import json

conn = sqlite3.connect('book.db')
cur = conn.cursor()

client = MongoClient('localhost', 27017)
db = client['bookstore']
book_col = db['books']

cur.execute("SELECT * FROM book")
books = cur.fetchall()

for i, record in enumerate(books):
    tags = list(str(record[15]).split("\n"))[:-1]
    if tags is None or tags == "":
        tags = []
    picture = list(str(record[16]).split("\n"))
    if len(picture) == 0:
        picture = []
    elif picture[-1] == '':
        picture = picture[0:-1]

    booki = {
        "id": record[0],
        "title": record[1],
        "author": record[2],
        "publisher": record[3],
        "original_title": record[4],
        "translator": record[5],
        "pub_year": record[6],
        "pages": record[7],
        "price": record[8],
        "currency_unit": record[9],
        "binding": record[10],
        "isbn": record[11],
        "author_intro": record[12],
        "book_intro": record[13],
        "content": record[14],
        "tags": record[15],
        "picture": record[16]
    }
    book_col.insert_one(booki)

print(f"{len(books)} books have been converted from SQL to mongoDB.")
conn.close()
client.close()
