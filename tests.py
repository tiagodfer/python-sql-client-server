import sqlite3

conn = sqlite3.connect('db/cnpj.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM socios WHERE nome LIKE ? AND cpf_cnpj LIKE ?", ('Tiago Dias Ferreira','%' + '515141' + '%',))
tables = cursor.fetchall()
print(tables)
conn.close()
