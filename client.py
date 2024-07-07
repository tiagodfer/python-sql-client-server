import socket

# client configuration
HEADER = 256
PORT = 5050
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

def menu():
    print("Menu:")
    print("1 - Search by Name")
    print("2 - Search by CPF")
    print("0 - Exit")
    choice = input("Enter your choice: ")
    return choice

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    while choice != '0' :
        choice = menu()
        if choice == '1':
            name = input("Enter name: ")
            #queries.search_cpf_by_name(name, cursor_cpf)
        elif choice == '2':
            cpf = input("Enter CPF: ")
            #queries.search_cpf_by_cpf(cpf, cursor_cpf)
    #conn_cnpj.close()
    #conn_cpf.close()
