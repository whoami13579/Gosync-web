import sqlite3
from werkzeug.security import generate_password_hash

con = sqlite3.connect("instance/database.db")
cur = con.cursor()

users = [
    (1, "administrator", None, generate_password_hash("111111"), None, None, 2),
    (2, "user1@gmail.com", "user1", generate_password_hash("111111"), "fcu", None, 1),
]
cur.executemany("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?)", users)
con.commit()
