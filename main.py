import sqlite3

conn = sqlite3.connect('db/cnpj.db')
cursor = conn.cursor()
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

for table_name, table_sql in tables:
    print(f"Table: {table_name}")
    print(table_sql)
    print("")
