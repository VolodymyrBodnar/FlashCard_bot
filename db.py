import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute('''CREATE TABLE users
             (name text, goal integer, id integer
        )''')

conn.commit()
conn.close()
