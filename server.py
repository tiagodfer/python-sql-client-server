import sqlite3
import json
import queries
import socket

def main():
    # SQL configuration
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/cpf.db')
    cursor_cnpj = conn_cnpj.cursor()
    cursor_cpf = conn_cpf.cursor()

    # server configuration
    HEADER = 256
    PORT = 5050
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (SERVER, PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    # starting server
    server.listen()
    while True:
        conn, addr = server.accept()

if __name__ == "__main__":
    main()
