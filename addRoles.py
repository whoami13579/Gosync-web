import sqlite3

con = sqlite3.connect("instance/database.db")
cur = con.cursor()

roles = [
    (1, "用戶"),
    (2, "管理員"),
]
cur.executemany("INSERT INTO roles VALUES(?, ?)", roles)
con.commit()
