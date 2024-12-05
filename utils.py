import base64
import pickle


class Utils:
    gmail_codings = {
        "INBOX": "INBOX",
        "[Gmail]": "[Gmail]",
        "[Gmail]/&BBIEMAQ2BD0EPgQ1-": "[Gmail]/Важное",
        "[Gmail]/&BBIEQQRP- &BD8EPgRHBEIEMA-": "[Gmail]/Все письма",
        "[Gmail]/&BBoEPgRABDcEOAQ9BDA-": "[Gmail]/Корзина",
        "[Gmail]/&BB4EQgQ,BEAEMAQyBDsENQQ9BD0ESwQ1-": "[Gmail]/Отправленные",
        "[Gmail]/&BB8EPgQ8BDUERwQ1BD0EPQRLBDU-": "[Gmail]/Помеченные",
        "[Gmail]/&BCEEPwQwBDw-": "[Gmail]/Спам",
        "[Gmail]/&BCcENQRABD0EPgQyBDgEOgQ4-": "[Gmail]/Черновики"
    }

    @staticmethod
    def encode_imap_folder_name(folder_name):
        utf16_bytes = folder_name.encode("utf-16-be")
        encoded_base64 = base64.b64encode(utf16_bytes).decode("ascii")

        encoded_base64 = encoded_base64.replace("/", ",")
        return "&" + encoded_base64 + "-"

    @staticmethod
    def decode_imap_folder_name(folder_name):
        folder_name = folder_name.strip("\"")

        if not folder_name.startswith("&"):
            return folder_name

        folder_name = folder_name[1:].rstrip("-")
        folder_name = folder_name.replace(",", "/")

        while len(folder_name) % 4 != 0:
            folder_name += "="
        decoded_bytes = base64.b64decode(folder_name)

        return decoded_bytes.decode("utf-16-be")

    @staticmethod
    def get_snippet(msg, max_length=50):
        snippet = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" and not part.get("Content-Disposition"):
                    snippet = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
                    break
        else:
            snippet = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8")
        return snippet[:max_length]

    @staticmethod
    def get_list_folders():
        with open("coded_folders.pkl", "rb") as table:
            data = pickle.load(table)
            return list(data.keys())
