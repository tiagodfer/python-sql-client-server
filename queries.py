import sqlite3
import json

def search_cpf_by_name(name, cursor):
    cursor.execute("SELECT * FROM cpf WHERE nome LIKE ?", ('%' + name + '%',))
    result = cursor.fetchall()
    json_result = []
    for row in result:
        json_dict = {
            'cpf': row[0],
            'nome': row[1],
            'sexo': row[2],
            'nasc': row[3]
            }
        json_result.append(json_dict)
    print(json.dumps(json_result, indent=2))

def search_cpf_by_cpf(cpf, cursor):
    cursor.execute("SELECT * FROM cpf WHERE cpf LIKE ?", ('%' + cpf + '%',))
    result = cursor.fetchall()
    json_result = []
    for row in result:
        json_dict = {
            'cpf': row[0],
            'nome': row[1],
            'sexo': row[2],
            'nasc': row[3]
            }
        json_result.append(json_dict)
    print(json.dumps(json_result, indent=2))
