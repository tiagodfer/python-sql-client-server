import sqlite3

conn = sqlite3.connect('db/cnpj.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM socios WHERE nome LIKE ?", ('%Tiago Dias Ferreira',))
tables = cursor.fetchall()
print(tables)
conn.close()
