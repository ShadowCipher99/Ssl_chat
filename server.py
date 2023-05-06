# Импортируем модуль SSL для создания безопасного подключения
import ssl

# Импортируем модуль threading для работы с нитями
import threading

# Импортируем модуль socket для работы с сетью
import socket

# Импортируем модуль os для работы с операционной системой
import os

# Импортируем модуль pyopenssl для генерации и использования сертификатов и ключей
from OpenSSL import crypto

# Создаем класс сервера
class Server:
    def __init__(self):
        # Проверяем наличие сертификата и ключа
        if not os.path.exists('server.crt') or not os.path.exists('server.key'):
            # Генерируем самоподписанный сертификат и ключ
            k = crypto.PKey() #генерация нового ключа
            k.generate_key(crypto.TYPE_RSA, 16384) #определение типа ключа и его длины
            cert = crypto.X509() #создание нового экземпляра класса X509 - цифрового сертификата
            cert.get_subject().CN = 'localhost' #задаем имя целевой системы
            cert.set_issuer(cert.get_subject()) #задаем данные об издателе
            cert.set_pubkey(k) #задаем открытый ключ в сертификат
            cert.gmtime_adj_notBefore(0) #задаем время начала действия сертификата
            cert.gmtime_adj_notAfter(365 * 24 * 60 * 60) #задаем время окончания действия сертификата
            cert.sign(k, "sha1") #подписываем сертификат
            with open("server.key", "wb") as key_file:
                key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k)) #записываем в файл содержимое ключа
            with open("server.crt", "wb") as cert_file:
                cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert)) #записываем в файл содержимое сертификата

        # Устанавливаем настройки сервера: адрес и порт, список соединений
        self.HOST = '127.0.0.1' #адрес сервера
        self.PORT = 9000 #порт сервера
        self.connections = [] #контактный список

        # Создаем сокет
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP

        # Оборачиваем сокет в SSL
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) #создаем SSL контекст
        context.load_cert_chain('server.crt', 'server.key') #загружаем сертификат и ключ
        self.s_ssl = context.wrap_socket(self.s, server_side=True) #оборачиваем сокет в SSL с указанием SSL контекста

    def start(self):
        # Подключаемся к порту и ожидаем клиента
        self.s_ssl.bind((self.HOST, self.PORT)) #назначаем данному сокету адрес и порт
        self.s_ssl.listen(1) #слушаем на подключения
        print('Server started') #выводим сообщение в консоль

        while True:
            # Подключаемся к порту и ожидаем клиента
            conn, addr = self.s_ssl.accept() #ожидаем входящее подключение

            # Добавляем соединение в список
            self.connections.append(conn)

            # Обрабатываем клиента в новом потоке
            threading.Thread(target=self.handle_client, args=(conn,)).start() #запускаем обработку клиента в отдельном потоке

    def handle_client(self, conn):
        while True:
            # Отправляем сообщения клиенту
            data = conn.recv(1024)  # получаем данные от клиента

            if data:
                sender = conn.getpeername() #узнаем адрес отправителя
                # Отправляем сообщение всем клиентам, кроме отправителя
                for client_conn in self.connections:
                    if client_conn != conn:
                        client_conn.sendall(('Client ' + str(sender) + ': ' + data.decode()).encode()) #шифруем и отправляем данные всем клиентам, кроме исходного
            else:
                conn.close()

                # Удаляем соединение из списка
                self.connections.remove(conn)
                break


# Создаем объект сервера и запускаем
server = Server()
server.start()
