from PyQt5 import QtWidgets, QtCore
import server
from multiprocessing import Manager
import multiprocessing

class ServerThread(QtCore.QThread):
    def __init__(self, server):
        super().__init__()
        self.server = server

    def run(self):
        self.server.start()

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python QT5 Server")
        self.setFixedSize(500, 160)
        self.cpf_db = None
        self.cnpj_db = None
        self.server = None
        self.semaphore = None
        self.manager = None

        # DB fields
        self.cpf_db_field = QtWidgets.QLineEdit()
        self.cpf_db_field.setReadOnly(True)
        self.cpf_db_field.setPlaceholderText("CPF database path")
        self.cpf_db_button = QtWidgets.QPushButton("set CPF database")

        self.cnpj_db_field = QtWidgets.QLineEdit()
        self.cnpj_db_field.setReadOnly(True)
        self.cnpj_db_field.setPlaceholderText("CNPJ database path")
        self.cnpj_db_button = QtWidgets.QPushButton("set CNPJ database")

        # Threads field
        self.threads_field = QtWidgets.QSpinBox()
        self.threads_field.setMinimum(1)
        self.threads_field.setMaximum(64)
        default_threads = multiprocessing.cpu_count()
        self.threads_field.setValue(default_threads)
        self.threads_field.setPrefix("Threads: ")

        # Port field
        self.port_field = QtWidgets.QLineEdit('5000')
        self.port_field.setPlaceholderText("Port")

        # Start/Stop and Close Buttons
        self.start_server_button = QtWidgets.QPushButton("Start Server")
        self.stop_server_button = QtWidgets.QPushButton("Stop Server")
        self.close_button = QtWidgets.QPushButton("Close")

        self.error_label = QtWidgets.QLabel("")
        self.error_label.setStyleSheet("color: red")
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.setWordWrap(True)

        # Layouts
        cpf_layout = QtWidgets.QHBoxLayout()
        cpf_layout.addWidget(self.cpf_db_field)
        cpf_layout.addWidget(self.cpf_db_button)

        cnpj_layout = QtWidgets.QHBoxLayout()
        cnpj_layout.addWidget(self.cnpj_db_field)
        cnpj_layout.addWidget(self.cnpj_db_button)

        hostport_layout = QtWidgets.QHBoxLayout()
        hostport_layout.addWidget(self.threads_field)
        hostport_layout.addWidget(self.port_field)

        error_layout = QtWidgets.QHBoxLayout()
        error_layout.addWidget(self.error_label)

        startstop_layout = QtWidgets.QHBoxLayout()
        startstop_layout.addWidget(self.start_server_button)
        startstop_layout.addWidget(self.stop_server_button)

        close_layout = QtWidgets.QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(self.close_button)
        close_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(cpf_layout)
        main_layout.addLayout(cnpj_layout)
        main_layout.addLayout(hostport_layout)
        main_layout.addLayout(error_layout)
        main_layout.addLayout(startstop_layout)
        main_layout.addLayout(close_layout)

        self.setLayout(main_layout)

        # Connect
        self.cpf_db_button.clicked.connect(self.select_cpf_db)
        self.cnpj_db_button.clicked.connect(self.select_cnpj_db)
        self.start_server_button.clicked.connect(self.start_server_handler)
        self.stop_server_button.clicked.connect(self.stop_server_handler)
        self.close_button.clicked.connect(self.close)

    def select_cpf_db(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select CPF Database")
        if path:
            self.cpf_db = path
            self.cpf_db_field.setText(path)
            print(f"CPF DB Selected: {path}")

    def select_cnpj_db(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select CNPJ Database")
        if path:
            self.cnpj_db = path
            self.cnpj_db_field.setText(path)
            print(f"CNPJ DB Selected: {path}")

    def start_server_handler(self):
        threads = self.threads_field.value()
        port = self.port_field.text().strip()
        if not port or not self.cpf_db or not self.cnpj_db:
            self.error_label.setText("Please fill all fields and select both databases.")
            return
        try:
            port = int(port)
        except ValueError:
            self.error_label.setText("Invalid port number")
            return
        self.manager = Manager()
        self.semaphore = self.manager.BoundedSemaphore(threads)
        self.server = server.Server(
            host = "0.0.0.0",
            port = int(port),
            cpf_db = self.cpf_db,
            cnpj_db = self.cnpj_db,
            semaphore = self.semaphore
        )
        self.server_thread = ServerThread(self.server)
        self.server_thread.start()

    def stop_server_handler(self):
        print("Server.stop() called.")
        if self.server:
            self.server.stop()
            print("Server stopped successfully.")
        if hasattr(self, 'server_thread') and self.server_thread.isRunning():
            self.server_thread.quit()
            self.server_thread.wait()
