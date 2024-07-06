import sqlite3
import json

def menu():
    print("Menu:")
    print("1 - Search by Name")
    print("2 - Search by CPF")
    print("0 - Exit")
    choice = input("Enter your choice: ")
    return choice

def main():
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/cpf.db')
    cursor_cnpj = conn_cnpj.cursor()
    cursor_cpf = conn_cpf.cursor()
    choice = 0

    while choice != '0' :
        choice = menu()
        if choice == '1':
            name = input("Enter name: ")
            cursor_cpf.execute("SELECT * FROM cpf WHERE nome LIKE ?", ('%' + name + '%',))
            result = cursor_cpf.fetchall()
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
        elif choice == '2':
            cpf = input("Enter CPF: ")
            cursor_cpf.execute("SELECT * FROM cpf WHERE cpf LIKE ?", ('%' + cpf + '%',))
            result = cursor_cpf.fetchall()
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


    conn_cnpj.close()
    conn_cpf.close()

if __name__ == "__main__":
    main()
