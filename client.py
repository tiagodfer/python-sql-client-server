import socket
import json

def menu():
    print("Menu:")
    print("1 - Search person in CPF database by name")
    print("2 - Search person in CPF database by exact name")
    print("3 - Search person in CPF database by CPF")
    print("4 - Search person in CNPJ database by name)")
    print("5 - Search person in CNPJ database by both name and CPF")
    print("0 - Exit")
    choice = input("Enter your choice: ")
    return choice

def main():
    # client configuration
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 5050
    FORMAT = 'utf-8'
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    while True:
        choice = menu()
        if choice == '1':
            name = input("Enter name: ")
            message = name + "nf"
            client.sendall(message.encode())
            data = client.recv(8192)
            result = data.decode()
            result = json.loads(result)
            result = json.dumps(result, indent=4)
            print(result)
        elif choice == '2':
            name = input("Enter exact name: ")
            message = name + "xf"
            client.sendall(message.encode())
            data = client.recv(8192)
            result = data.decode()
            result = json.loads(result)
            result = json.dumps(result, indent=4)
            print(result)
        elif choice == '3':
            cpf = input("Enter CPF: ")
            message = cpf + "cf"
            client.sendall(message.encode())
            data = client.recv(8192)
            result = data.decode()
            result = json.loads(result)
            result = json.dumps(result, indent=4)
            print(result)
        elif choice == '4':
            cpf = input("Enter Name: ")
            message = cpf + "nj"
            client.sendall(message.encode())
            data = client.recv(8192000)
            result = data.decode()
            result = json.loads(result)
            result = json.dumps(result, indent=4)
            print(result)
        elif choice == '5':
            cpf = input("Enter Name: ")
            message = cpf + "nj"
            client.sendall(message.encode())
            data = client.recv(81920000)
            result = data.decode()
            result = json.loads(result)
            result = json.dumps(result, indent=4)
            print(result)
        elif choice == '0':
            break
    message = "e"
    client.sendall(message.encode())
    client.close()

if __name__ == "__main__":
    main()
