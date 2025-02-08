from sqlite3 import connect


__all__ = ['queries']


conn = connect("./DB/db.db")
with conn:
    cursor = conn.cursor()
    cursor.execute("""
           CREATE TABLE IF NOT EXISTS queries (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               query TEXT NOT NULL
           )
       """)
    cursor.execute("""
           CREATE TABLE IF NOT EXISTS weapon_list (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               page_id TEXT NOT NULL,
               url TEXT NOT NULL
           )
       """)
    conn.commit()
