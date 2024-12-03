import re
import email
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QListWidget, QTextEdit, QComboBox, QMessageBox)
from email.header import decode_header
from utils import Utils


class MainClientGUI(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setWindowTitle('IMAP Клиент')
        self.setGeometry(100, 100, 1500, 800)

        layout = QVBoxLayout()

        self.folder_combo = QComboBox()
        self.folder_combo.addItems(Utils.get_list_folders())
        layout.addWidget(self.folder_combo)

        self.email_list = QListWidget()
        layout.addWidget(self.email_list)

        refresh_button = QPushButton('Обновить список писем')
        refresh_button.clicked.connect(self.update_email)
        layout.addWidget(refresh_button)

        self.email_content = QTextEdit()
        self.email_content.setReadOnly(True)
        layout.addWidget(self.email_content)

        read_button = QPushButton('Прочитать письмо')
        read_button.clicked.connect(self.read_email)
        layout.addWidget(read_button)

        read_button = QPushButton('Удалить письмо')
        read_button.clicked.connect(self.delete_email)
        layout.addWidget(read_button)

        send_layout = QHBoxLayout()
        self.to_line = QLineEdit()
        self.to_line.setPlaceholderText('Кому')
        send_layout.addWidget(self.to_line)

        self.subject_line = QLineEdit()
        self.subject_line.setPlaceholderText('Тема')
        send_layout.addWidget(self.subject_line)

        self.body_text = QTextEdit()
        self.body_text.setPlaceholderText('Текст письма')
        send_layout.addWidget(self.body_text)

        send_button = QPushButton('Отправить письмо')
        send_button.clicked.connect(self.send_email)
        send_layout.addWidget(send_button)

        layout.addLayout(send_layout)

        self.setLayout(layout)

    def update_email(self):
        folder = self.folder_combo.currentText()
        message_ids = self.client.fetch_emails(folder)
        self.email_list.clear()
        for msg_id in message_ids:
            status, msg_data = self.client.mail.fetch(msg_id, "(RFC822)")
            if status == "OK":
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8")
                        sender = msg.get("From")
                        snippet = Utils.get_snippet(msg)
                        index = sender.find("<")
                        self.email_list.addItem(f"ID: {msg_id},"
                                                f" От: {sender[index:]}, "
                                                f"Тема: {subject}, "
                                                f"Начало: {snippet}")

    def read_email(self):
        selected_item = self.email_list.currentItem()
        if selected_item:
            try:
                email_id = selected_item.text().split(",")[0].split(":")[1].strip().replace('b', "").strip('\'')
                folder = self.folder_combo.currentText()
                content = re.sub(r"<[a-z/=\"]*>", "\n", self.client.read_email(folder, email_id))

                self.email_content.setPlainText(content)
            except Exception as e:
                QMessageBox.warning(self, 'Ёмоё', f'Не удалось прочитать письмо: {str(e)}')

    def delete_email(self):
        selected_item = self.email_list.currentItem()
        if selected_item:
            try:
                email_id = selected_item.text().split(",")[0].split(":")[1].strip().replace(
                    'b', "").strip('\'')
                folder = self.folder_combo.currentText()

                self.client.delete_email(folder, email_id)
                self.email_list.takeItem(self.email_list.row(selected_item))
            except Exception as e:
                QMessageBox.warning(self, 'Ёмоё', f'Не удалось удалить письмо: {str(e)}')

    def send_email(self):
        to_address = self.to_line.text()
        subject = self.subject_line.text()
        body = self.body_text.toPlainText()

        if to_address and subject and body:
            self.client.upload_email(subject, body, to_address)
            QMessageBox.information(self, 'Ура', 'Письмо отправлено')
        else:
            QMessageBox.warning(self, 'Ёперный театр', 'Заполните все поля')

    def closeEvent(self, event):
        self.client.logout()
        event.accept()
