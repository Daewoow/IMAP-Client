import bs4
import email
import imaplib
import os
import pickle
import smtplib
import ssl
import re
import time
from PyQt5.QtWidgets import QMessageBox
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils import Utils


ALPHABET = ["qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"]


class ConnectedClient:
    def __init__(self, widget, server, port, login, password):
        self.widget = widget
        self.server = server
        self.port = port
        self.login = login
        self.password = password
        self.mail = None
        self.coded_encoded = dict()

    def connect_imap(self):
        self.mail = imaplib.IMAP4_SSL(self.server, self.port)
        self.mail.login(self.login, self.password)

    def fill_folders_names(self):
        status, mailboxes = self.mail.list()
        if status == "OK":
            for mailbox in mailboxes:
                mailbox_info = mailbox.decode()
                flags, delimiter, mailbox_name = mailbox_info.split(maxsplit=2)
                if isinstance(mailbox_name, bytes):
                    mailbox_name = mailbox_name.decode('utf-8')
                decoded_mailbox_name = Utils.decode_imap_folder_name(mailbox_name)
                self.coded_encoded[decoded_mailbox_name] = mailbox_name
            with open("coded_folders.pkl", "wb") as table:
                pickle.dump(self.coded_encoded, table)
        else:
            QMessageBox.warning(self.widget, 'Ёмоё', f'Не удалось получить список ящиков')

    def fetch_emails(self, folder):
        if folder[0] not in ALPHABET[0]:
            folder = self.coded_encoded[folder]

        status, _ = self.mail.select(folder)
        if status != "OK":
            QMessageBox.warning(self.widget, 'Ёмоё', f'Не удалось выбрать папку')
            return []

        status, messages = self.mail.search(None, "ALL")
        if status == "OK":
            message_ids = messages[0].split()
            return message_ids
        else:
            QMessageBox.warning(self.widget, 'Ёмоё', f'Не удалось получить содержимое папки')
            return []

    def read_email(self, folder, email_id):
        email_id = email_id.strip()

        if folder not in ALPHABET[0]:
            folder = self.coded_encoded.get(folder, folder)

        status, _ = self.mail.select(folder)
        if status != "OK":
            QMessageBox.warning(self.widget, 'Ёмоё', f'Не удалось выбрать папку')
            return

        status, msg_data = self.mail.fetch(email_id, "(RFC822)")
        if status == "OK":
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    body = ""
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = part.get("Content-Disposition")

                        if content_type == "text/plain" and not content_disposition:
                            try:
                                body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
                            except (UnicodeDecodeError, AttributeError):
                                QMessageBox.warning(self.widget, 'Ёмоё', f'Проблемки с декодированием')

                        elif content_type == "text/html" and not content_disposition:
                            try:
                                html_body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
                                soup = bs4.BeautifulSoup(html_body, "html.parser")
                                body = soup.get_text()
                            except (UnicodeDecodeError, AttributeError):
                                QMessageBox.warning(self.widget, 'Ёмоё', f'Проблемки с декодированием')

                        elif content_disposition and "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                decoded_filename, encoding = decode_header(filename)[0]
                                if isinstance(decoded_filename, bytes):
                                    decoded_filename = decoded_filename.decode(encoding or "utf-8")

                                decoded_filename = re.sub(r'[<>:"/\\|?*]', '', decoded_filename)

                                filepath = os.path.join(".", decoded_filename)
                                with open(filepath, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                QMessageBox.information(self.widget, "Ура", f"Вложение сохранено как {filepath}")

                    return body
        else:
            QMessageBox.warning(self.widget, "Ёмоё", "Не получилось прочитать письмо")

    def upload_email(self, subject, body, to_address):
        msg = MIMEMultipart()
        msg["From"] = self.login
        msg["To"] = to_address
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))
        smtp_server = self.server.replace("imap", "smtp")
        try:
            with smtplib.SMTP_SSL(smtp_server, 465) as smtp:
                context = ssl.create_default_context()
                try:
                    smtp.starttls(context=context)
                except Exception:
                    pass
                smtp.ehlo()
                smtp.login(self.login, self.password)
                smtp.sendmail(self.login, to_address, msg.as_string())
        except Exception as e:
            QMessageBox(self.widget, "Ёмоё", "Не отправилось")

        if self.server == "imap.mail.ru":
            self.mail.select(self.coded_encoded["Отправленные"])
            self.mail.append(self.coded_encoded["Отправленные"], None,
                             imaplib.Time2Internaldate(time.time()), msg.as_bytes())

    def delete_email(self, folder, email_id):
        email_id = email_id.strip()

        if folder not in ALPHABET[0]:
            folder = self.coded_encoded.get(folder, folder)

        trash_folder = self.coded_encoded.get("Корзина", None)
        if not trash_folder:
            QMessageBox.warning(self.widget, "Ёмоё", "Папка 'Корзина' не найдена")
            return

        status, _ = self.mail.select(folder)
        if status != "OK":
            QMessageBox.warning(self.widget, 'Ёмоё', f'Не удалось выбрать папку для удаления')
            return

        try:
            result = self.mail.copy(email_id, trash_folder)
            if result[0] != "OK":
                QMessageBox.warning(self.widget, "Ёмоё", f"Не удалось переместить письмо {email_id} в 'Корзина'")
                return

            status, _ = self.mail.store(email_id, '+FLAGS', '\\Deleted')
            if status == "OK":
                self.mail.expunge()
                QMessageBox.information(self.widget, "Ура", f"Письмо {email_id} успешно перемещено в 'Корзина'")
            else:
                QMessageBox.warning(self.widget, "Ёмоё", f"Не удалось пометить письмо {email_id} как удалённое")
        except Exception as e:
            QMessageBox.warning(self.widget, "Ёмоё", f"Произошла ошибка при перемещении: {str(e)}")

    def logout(self):
        if self.mail:
            self.mail.logout()
