import sqlite3

con = sqlite3.connect("instance/database.db")
cur = con.cursor()

forums = [
    (1, "搭車", "一起搭車", None),
    (2, "打球", "一起打球", None),
    (3, "釣魚", "一起釣魚", None),
    (4, "打羽球", "一起打羽球", None),
]
cur.executemany("INSERT INTO forums VALUES(?, ?, ?, ?)", forums)
con.commit()
