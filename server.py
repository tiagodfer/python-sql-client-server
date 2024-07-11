import sqlite3
import json
import queries
import socket
import multiprocessing
import select
import time

def handle(conn, cursor_cpf, cursor_cnpj):
            data = conn.recv(1024)
            query = data.decode()
            if query[-1] == 'f':
                if query[-2] == 'n':
                    result = queries.search_cpf_by_name(query[:-2], cursor_cpf)
                    conn.sendall(result.encode())
                elif query[-2] == 'x':
                    result = queries.search_cpf_by_exact_name(query[:-2], cursor_cpf)
                    conn.sendall(result.encode())
                elif query[-2] == 'c':
                    result = queries.search_cpf_by_cpf(query[:-2], cursor_cpf)
                    conn.sendall(result.encode())
            elif query[-1] == 'j':
                if query[-2] == 'n':
                    result = queries.check_person_cnpj(query[:-2], cursor_cnpj)
                    conn.sendall(result.encode())
                elif query[-2] == 'x':
                    result = queries.check_person_cnpj_and_cpf(query[:-2], cursor_cnpj)
                    conn.sendall(result.encode())

def main():
    # SQL configuration
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/cpf.db')
    cursor_cnpj = conn_cnpj.cursor()
    cursor_cpf = conn_cpf.cursor()

    # server configuration
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 5050
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.settimeout(60)
    server.bind((HOST, PORT))

    # starting server
    server.listen()

    last = time.time()
    while True:
        loop, _, _ = select.select([server], [], [], 60)
        if loop:
            conn, addr = server.accept()
            handler = multiprocessing.Process(target=handle, args=(conn, cursor_cpf, cursor_cnpj,))
            handler.start()
            conn.close()
            last = time.time()
        else:
            if time.time() - last >= 60:
                break
    server.close()
    conn_cnpj.close()
    conn_cpf.close()

if __name__ == "__main__":
    main()
