import socket
import threading
import ssl
import secrets
import curses

class ChatApp:
    def __init__(self):
        self.HOST = input("host:")
        self.PORT = 443
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.load_verify_locations('server.crt')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_ssl = self.context.wrap_socket(self.sock, server_hostname=self.HOST)

        # Список цветов для разных отправителей
        self.colors = [curses.COLOR_RED, curses.COLOR_GREEN, curses.COLOR_BLUE, curses.COLOR_YELLOW, curses.COLOR_MAGENTA, curses.COLOR_CYAN]
        self.sender_colors = {}  # Словарь для хранения цветов отправителей

    def encrypt(self, msg, key):
        crypt = ''
        for i in range(len(msg)):
            crypt += str(ord(msg[i]) ^ ord(key[i])) + " "  # Добавляем пробел после каждого преобразованного символа
        return crypt

    def decrypt(self, crypt, key):
        key = key.decode('utf-8')
        message = ''
        crypt_list = crypt.split()
        for i in range(len(crypt_list)):
            message += chr(int(crypt_list[i]) ^ ord(key[i % len(key)]))
        return message

    def receive(self, stdscr):
        while True:
            key = self.sock_ssl.recv(1024)
            data = self.sock_ssl.recv(1024)
            decrypt_message = self.decrypt(data.decode('utf-8'), key)
            sender = key.decode('utf-8')  # Читаем отправителя из ключа

            # Проверяем, есть ли цвет для отправителя
            if sender not in self.sender_colors:
                # Генерируем новый цвет для отправителя
                color_pair = len(self.sender_colors) % len(self.colors) + 1
                curses.init_pair(color_pair, self.colors[color_pair % len(self.colors)], curses.COLOR_BLACK)
                self.sender_colors[sender] = curses.color_pair(color_pair)

            stdscr.addstr(decrypt_message + '\n', self.sender_colors[sender])
            stdscr.refresh()

    def start(self, stdscr):
        self.sock_ssl.connect((self.HOST, self.PORT))
        stdscr.addstr('Connected to server\n 'Welcome to RENCIR Chat'')
        stdscr.refresh()

        receive_thread = threading.Thread(target=self.receive, args=(stdscr,))
        receive_thread.start()

        while True:
            msg = stdscr.getstr().decode('utf-8')
            key = ''.join(chr(secrets.choice(range(65, 90))) for _ in range(len(msg)))
            encrypt_message = self.encrypt(msg, key)
            self.sock_ssl.sendall(key.encode('utf-8'))
            self.sock_ssl.sendall(encrypt_message.encode('utf-8'))

    def main(self):
        stdscr = curses.initscr()
        curses.cbreak()
        stdscr.keypad(True)
        curses.start_color()  # Включаем поддержку цветов

        try:
            self.start(stdscr)
        finally:
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()


if __name__ == '__main__':
    chat_app = ChatApp()
    chat_app.main()
