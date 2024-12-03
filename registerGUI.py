from PyQt5.QtWidgets import (QWidget, QLineEdit, QPushButton, QMessageBox, QFormLayout)
from connectedClient import ConnectedClient
from mainClientGUI import MainClientGUI


class RegisterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Авторизация')
        self.setGeometry(810, 340, 300, 300)

        layout = QFormLayout()

        self.server_input = QLineEdit()
        self.port_input = QLineEdit()
        self.login_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addRow('Сервер:', self.server_input)
        layout.addRow('Порт:', self.port_input)
        layout.addRow('Логин:', self.login_input)
        layout.addRow('Пароль:', self.password_input)

        login_button = QPushButton('Войти')
        login_button.clicked.connect(self.login)
        layout.addRow(login_button)

        self.setLayout(layout)

    def login(self):
        server = self.server_input.text()
        port = int(self.port_input.text())
        login = self.login_input.text()
        password = self.password_input.text()

        try:
            self.client = ConnectedClient(self, server, port, login, password)
            self.client.connect_imap()
            self.client.fill_folders_names()
            self.main_window = MainClientGUI(self.client)
            self.main_window.show()
            self.close()
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Не удалось подключиться: {str(e)}')