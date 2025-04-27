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
    conn_cpf = sqlite3.connect('db/basecpf.db')
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
            conn_cpf.close()
            conn_cnpj.close()

class Window(QtWidgets.QWidget):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.setWindowTitle("Python QT6 Server")
        self.setFixedSize(500, 160)

        # Buttons
        self.cpf_db_button = QtWidgets.QPushButton("CPF DB")
        self.cnpj_db_button = QtWidgets.QPushButton("CNPJ DB")
        self.start_server_button = QtWidgets.QPushButton("Start Server")
        self.stop_server_button = QtWidgets.QPushButton("Stop Server")
        self.close_button = QtWidgets.QPushButton("Close")

        # Fields
        self.host_input = QtWidgets.QLineEdit()
        self.host_input.setPlaceholderText("Host (e.g. 127.0.0.1)")
        self.host_input.setText("127.0.0.1")
        self.port_input = QtWidgets.QLineEdit()
        self.port_input.setPlaceholderText("Port (e.g. 5050)")

        # Layout
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.cpf_db_button)
        top_layout.addWidget(self.cnpj_db_button)
        top_layout.addWidget(self.host_input)
        top_layout.addWidget(self.port_input)
        top_layout.addWidget(self.start_server_button)
        top_layout.addWidget(self.stop_server_button)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.close_button)
        bottom_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

        # State
        self.cpf_db_path = None
        self.cnpj_db_path = None

        # Connect signals
        self.cpf_db_button.clicked.connect(self.select_cpf_db)
        self.cnpj_db_button.clicked.connect(self.select_cnpj_db)
        self.start_server_button.clicked.connect(self.start_server_handler)
        self.stop_server_button.clicked.connect(self.stop_server_handler)
        self.close_button.clicked.connect(self.close)

    def select_cpf_db(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select CPF Database")
        if path:
            self.cpf_db_path = path
            print(f"CPF DB Selected: {path}")

    def select_cnpj_db(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select CNPJ Database")
        if path:
            self.cnpj_db_path = path
            print(f"CNPJ DB Selected: {path}")

    def start_server_handler(self):
        host = self.host_input.text().strip()
        port = self.port_input.text().strip()
        if not host or not port:
            print("Host/Port cannot be empty!")
            return
        if not self.cpf_db_path or not self.cnpj_db_path:
            print("Select both databases first!")
            return
        try:
            port = int(port)
        except ValueError:
            print("Invalid port number")
            return
        self.server.start(host, port, self.cpf_db_path, self.cnpj_db_path)

    def stop_server_handler(self):
        self.server.stop()

if __name__ == "__main__":
    main()
