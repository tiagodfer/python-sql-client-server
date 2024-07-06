import sqlite3

def menu():
    print("Menu:")
    print("1 - Search by Name")
    print("2 - Search by CPF")
    print("0 - Exit")
    choice = input("Enter your choice (1/2/3): ")
    return choice

def main():
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/cpf.db')
    cursor_cnpj = conn_cnpj.cursor()
    cursor_cpf = conn_cpf.cursor()
    choice = 0

    while choice != '0' :
        choice = menu()

    conn_cnpj.close()
    conn_cpf.close()

if __name__ == "__main__":
    main()
