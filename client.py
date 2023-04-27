# Импортируем модуль socket для использования сетевых функций
import socket
# Импортируем модуль ssl для шифрования передачи данных
import ssl
# Импортируем модуль click для удобного взаимодействия с пользователем из консоли
import click
# Импортируем модуль os для очистки консоли перед запуском приложения
import os
# Создаем класс Server для работы с клиентом
class Server:
    # Создаем метод init для инициализации класса
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # Создаем сокет
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Создаем контекст SSL
        self.ssl_context = ssl.create_default_context()
        # Отключаем проверку имени хоста
        self.ssl_context.check_hostname = False
        # Задаем режим проверки сертификата
        self.ssl_context.verify_mode = ssl.CERT_NONE
        # Оборачиваем сокет в SSL
        self.s_ssl = self.ssl_context.wrap_socket(self.s, server_hostname=self.host)

    # Метод connect для установки соединения с сервером
    def connect(self):
        self.s_ssl.connect((self.host, self.port))
        click.echo(click.style(f"Connected to {self.host} on port {self.port}", fg="green"))

    # Метод для отправки сообщений на сервер
    def send_message(self, message):
        self.s_ssl.sendall(message.encode())
        data = self.s_ssl.recv(1024)
        if data:
            click.echo(click.style(f"Received: {data.decode()}", fg="yellow"))
        else:
            click.echo(click.style("Server disconnected", fg="red"))
            self.disconnect()

    # Метод для закрытия соединения
    def disconnect(self):
        self.s_ssl.close()

# Задаем команду клиентского приложения с опциями хоста и порта
@click.command()
@click.option('-h', '--host', default='0.0.0.0', help='The host to connect to.')
@click.option('-p', '--port', default=9000, help='The port to connect to.')
def run(host, port):
    # Создаем экземпляр сервера и устанавливаем соединение
    server = Server(host, port)
    server.connect()

    # Запускаем бесконечный цикл отправки сообщений
    while True:
        message = input('Client: ')
        server.send_message(message)

if __name__ == '__main__':
    # Очищаем консоль и выводим приветственное сообщение
    os.system("clear")
    print("Welcome to SLX chat!")
    # Запускаем клиентское приложение
    run()
