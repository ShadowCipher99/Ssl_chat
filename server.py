# Импорт модуля SSL - протокол безопасной передачи данных
import ssl
# Импорт модуля нитей
import threading
# Импорт модуля сокетов для работы с сетью
import socket
# Импорт модуля ОС для работы с операционной системой
import os

# Создание класса сервера
class Server:
    def __init__(self):
        # Проверка наличия сертификата и ключа
        if not os.path.exists('server.crt') or not os.path.exists('server.key'):
            # Генерация самоподписанного сертификата и ключа
            os.system('openssl ecparam -genkey -name secp521r1 -noout -out server.key')
            os.system('openssl req -new -key server.key -x509 -sha512 -days 365 -out server.crt')

        # Установка настроек сервера: адрес и порт, список соединений
        self.HOST = '192.168.0.2' # Подключение ко всем адресам сети
        self.PORT = 8080
        self.connections = []

        # Создание сокета
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Оборачиваем сокет в SSL - SSL контекст
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain('server.crt', 'server.key')
        self.s_ssl = ssl_context.wrap_socket(self.s, server_side=True) # Сокет, созданный с помощью ssl контекста

    def start(self):
        # Подключение к порту и ожидание клиента
        self.s_ssl.bind((self.HOST, self.PORT))
        self.s_ssl.listen(1) #слушаем порт на подключения
        print('Server started')

        while True:
            # Подключение к порту и ожидание клиента
            conn, addr = self.s_ssl.accept() #Принимаем входящее соединение, в том числе SSL
            print('Client connected:', addr)

            # Добавление соединения в список
            self.connections.append(conn)

            # Обрабатываем клиента в новом потоке
            threading.Thread(target=self.handle_client, args=(conn,)).start()

    def handle_client(self, conn):
        # Определение адреса отправителя
        sender = conn.getpeername()
        print('Sender:', sender)

        # Отправляем сообщения клиенту
        while True:
            data = conn.recv(1024) #1024 - максимальный размер передаваемых данных
            if data:
                print('Received:', data.decode()) #декодирование байтов данных

                # Отправляем сообщение всем клиентам кроме отправителя
                for client_conn in self.connections:
                    if client_conn != conn:
                        client_conn.sendall(('Client ' + str(sender) + ': ' + data.decode()).encode()) #шифрование и отправка данных, если соединение не является исходным

            else:
                print('Client disconnected:', sender)
                conn.close()

                # Удаление соединения из списка
                self.connections.remove(conn)
                break

# Создание объекта сервера и запуск
server = Server()
server.start()
