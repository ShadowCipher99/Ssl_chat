# импортируем модуль socket для работы с сетевыми соединениями
import socket
# импортируем модуль ssl для использования защищенного сокета
import ssl
# импортируем модуль click для работы с командной строкой
import click
# импортируем модуль os для работы с операционной системой

# создаем класс Server для работы с сервером и сокетом
class Server:
    # создаем конструктор класса для инициализации переменных и создания объекта сокета
    def __init__(self, host, port):
        # инициализируем переменные host и port
        self.host = host
        self.port = port
        # создаем объект сокета, AF_INET указывает на использование сетевого протокола IPv4,
        # а SOCK_STREAM - на использование потокового сокета
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # создаем объект защищенного сокета с помощью модуля ssl и настроек по умолчанию
        self.ssl_context = ssl.create_default_context()
        # отключаем проверку имени хоста
        self.ssl_context.check_hostname = False
        # отключаем проверку сертификата, так как мы работаем в локальной сети
        self.ssl_context.verify_mode = ssl.CERT_NONE
        # оборачиваем обычный сокет в защищенный с помощью ssl_context
        # указываем server_hostname, чтобы определить надежность соединения
        self.s_ssl = self.ssl_context.wrap_socket(self.s, server_hostname=self.host)

    # создаем метод для установки соединения с сервером
    def connect(self):
        self.s_ssl.connect((self.host, self.port))
        click.echo(click.style(f"Connected to {self.host} on port {self.port}", fg="green"))

    # создаем метод для отправки сообщения на сервер
    def send_message(self, message):
        # отправляем сообщение в защищенном сокете
        self.s_ssl.sendall(message.encode())
        # получаем ответ от сервера, если он есть
        data = self.s_ssl.recv(1024)
        if data:
            click.echo(click.style(f"Received: {data.decode()}", fg="yellow"))
        else:
            click.echo(click.style("Server disconnected", fg="red"))
            self.disconnect()

    # создаем метод для отключения от сервера
    def disconnect(self):
        self.s_ssl.close()

# создаем команду run, которая будет запускать клиентское приложение
@click.command()
# создаем опции командной строки для указания хоста и порта
@click.option('-h', '--host', default='127.0.0.1', help='The host to connect to.')
@click.option('-p', '--port', default=9000, help='The port to connect to.')
def run(host, port):
    # создаем объект класса Server и передаем ему хост и порт
    server = Server(host, port)
    # устанавливаем соединение с сервером
    server.connect()

    # создаем цикл для отправки сообщений на сервер
    while True:
        message = input('Client: ')
        server.send_message(message)

# проверяем, что код запускается как основной файл программы
if __name__ == '__main__':
    # очищаем консоль
    os.system("cls" if os.name == "nt" else "clear")
    # приветствуем пользователя
    print("Welcome to SLX chat!")
    # запускаем клиентское приложение
    run()
