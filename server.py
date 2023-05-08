# Импорт необходимых модулей
import ssl # модуль SSL-шифрования
import threading # модуль для создания параллельных потоков
import socket # модуль для работы с сокетами
import os # модуль для работы с операционной системой
from OpenSSL import crypto # модуль для генерации сертификатов и ключей через OpenSSL
import socks # модуль для подключения к сети Tor (анонимный доступ к серверу)
import socket as sock # модуль для работы с сокетами

# Создание класса сервера
class Server:
    def init(self):
        # Подключение к сети Tor для обеспечения анонимности
        socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
        sock.socket = socks.socksocket

        # Проверка наличия сертификата и ключа
        if not os.path.exists('server.crt') or not os.path.exists('server.key'):
            # Генерация самоподписанного сертификата и ключа
            k = crypto.PKey()
            k.generate_key(crypto.TYPE_RSA, 16384)
            cert = crypto.X509()
            cert.get_subject().CN = 'localhost'
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(k)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)
            cert.sign(k, "sha1")
            with open("server.key", "wb") as key_file:
                key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
            with open("server.crt", "wb") as cert_file:
                cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        # Установка настроек сервера: адрес и порт, список соединений
        self.HOST = '127.0.0.1' # адрес сервера
        self.PORT = 9000 # порт сервера
        self.connections = [] # список соединений

        # Создание сокета
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Оборачиваем сокет в SSL - SSL контекст
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('server.crt', 'server.key')
        self.s_ssl = context.wrap_socket(self.s, server_side=True) # Сокет, созданный с помощью SSL контекста

    def start(self):
        # Подключение к порту и ожидание клиента
        self.s_ssl.bind((self.HOST, self.PORT)) # связываем сокет с адресом и портом
        self.s_ssl.listen(1) #слушаем порт на подключения
        print('Server started') # вывод информации о начале работы сервера

        while True:
            # Подключение к порту и ожидание клиента
            conn, addr = self.s_ssl.accept() #Принимаем входящее соединение, в том числе SSL
            
            # Добавление соединения в список
            self.connections.append(conn)

            # Обрабатываем клиента в новом потоке
            threading.Thread(target=self.handle_client, args=(conn,)).start()

    def handle_client(self, conn):
        while True:
            # Отправляем сообщения клиенту
            data = conn.recv(1024)  # 1024 - максимальный размер передаваемых данных

            if data:
                sender = conn.getpeername() # получаем адрес отправителя
                # Отправляем сообщение всем клиентам кроме отправителя
                for client_conn in self.connections:
                    if client_conn != conn:
                        # шифрование и отправка данных, если соединение не является исходным
                        client_conn.sendall(('Client ' + str(sender) + ': ' + data.decode()).encode()) 
            else:
                conn.close()

                # Удаление соединения из списка
                self.connections.remove(conn)
                break

# Создание объекта сервера и запуск
server = Server()
server.start()
