import sqlite3 as sq

with sq.connect("test.db") as con:
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
    name TEXT
    )    
    """)