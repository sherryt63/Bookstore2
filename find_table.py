import sqlite3

conn = sqlite3.connect("book.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tags'")
print("Book table exists:" if cursor.fetchone() else "Book table does not exist.")
conn.close()