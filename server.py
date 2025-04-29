import sqlite3
import json
import queries
import socket
import multiprocessing
import re
import select
import urllib.parse

class Server():
    def __init__(self, host, port, cpf_db, cnpj_db, threads):
        super().__init__()
        self.host = host
        self.port = port
        self.cpf_db = cpf_db
        self.cnpj_db = cnpj_db
        self.server = None
        self.running = False
        self.semaphore = multiprocessing.BoundedSemaphore(threads)

    @staticmethod
    def send_http_json(conn, data):
        body = json.dumps(data)
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n"
            "\r\n"
            f"{body}"
        )
        conn.sendall(response.encode("utf-8"))
        print(response.encode("utf-8"))

    @staticmethod
    def handle(conn, cpf_db, cnpj_db, semaphore):
        # SQL configuration
        conn_cpf = sqlite3.connect(cpf_db)
        conn_cnpj = sqlite3.connect(cnpj_db)
        cursor_cpf = conn_cpf.cursor()
        cursor_cnpj = conn_cnpj.cursor()

        data = conn.recv(1024)
        request = data.decode()
        print(f"[SERVER] Received request: {request!r}")

        # /get-person-by-name/<name>
        match = re.match(r"GET /get-person-by-name/([^ ]+) HTTP/1.[01]", request)
        if match:
            name = match.group(1)
            name = urllib.parse.unquote_plus(name)
            print(f"[SERVER] Parsed name: {name}")
            result = queries.search_cpf_by_name(name, cursor_cpf)
            print(result)
            Server.send_http_json(conn, {"results": result})
            print("[SERVER] Sent HTTP JSON response.")
            semaphore.release()
            return

        # /get-person-by-exact-name/<name>
        match = re.match(r"GET /get-person-by-exact-name/([^ ]+) HTTP/1.[01]", request)
        if match:
            name = match.group(1)
            name = urllib.parse.unquote_plus(name)
            print(f"[SERVER] Parsed exact name: {name}")
            result = queries.search_cpf_by_exact_name(name, cursor_cpf)
            print(result)
            Server.send_http_json(conn, {"results": result})
            print("[SERVER] Sent HTTP JSON response.")
            semaphore.release()
            return

        # /get-person-by-cpf/<cpf>
        match = re.match(r"GET /get-person-by-cpf/(\d+) HTTP/1.[01]", request)
        if match:
            cpf = match.group(1)
            print(f"[SERVER] Parsed CPF: {cpf}")
            result = queries.search_cpf_by_cpf(cpf, cursor_cpf)
            print(result)
            Server.send_http_json(conn, {"results": result})
            print("[SERVER] Sent HTTP JSON response.")
            semaphore.release()
            return

        # none
        error_body = json.dumps({"error": "Invalid request"})
        response = (
            "HTTP/1.1 400 Bad Request\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(error_body)}\r\n"
            "\r\n"
            f"{error_body}"
        )
        conn.sendall(response.encode("utf-8"))
        print("[SERVER] Sent 400 Bad Request.")
        semaphore.release()

    def start(self):
        # server configuration
        HOST = self.host
        PORT = self.port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))

        # starting server
        self.running = True
        self.server.listen()

        while self.running:
            ready_to_read, _, _ = select.select([self.server], [], [], 1.0)
            if ready_to_read:
                try:
                    conn, addr = self.server.accept()
                except OSError:
                    break
                self.semaphore.acquire()
                handler = multiprocessing.Process(target=self.handle, args=(conn, self.cpf_db, self.cnpj_db, self.semaphore))
                handler.start()
                conn.close()
            else:
                continue

    def stop(self):
        self.running = False
        if self.server:
            self.server.close()
