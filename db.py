import sqlite3

connection = sqlite3.connect('employee.db')
c = connection.cursor()

# c.execute("""CREATE TABLE employees (
#         first text,
#         last text,
#         pay integer
#     )""")

c.execute('INSERT INTO employees VALUES("Corey","Shaffer",1000)')



connection.commit()

connection.close()

