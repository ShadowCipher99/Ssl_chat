import os
import socket
import ssl
import threading
from OpenSSL import crypto
import keyring

KEYRING_SERVICE_NAME = 'My Enigma Server'

# Функция для сохранения ключа в безопасное хранилище
def save_key_to_keyring(key):
    keyring.set_password(KEYRING_SERVICE_NAME, 'server_key', key)

# Функция для загрузки ключа из безопасного хранилища
def load_key_from_keyring():
    return keyring.get_password(KEYRING_SERVICE_NAME, 'server_key')


if not os.path.exists('server.crt') or not os.path.exists('server.key'):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 8192)
    cert = crypto.X509()
    cert_version = 2
    cert.set_version(cert_version)
    cert.get_subject().CN = b'localhost'
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(3600) 
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    ip_address = socket.gethostbyname(socket.gethostname())
    cert.add_extensions([
        crypto.X509Extension(b'subjectAltName', False,
                             b','.join([b'DNS:localhost', f'IP:{ip_address}'.encode()])),
        crypto.X509Extension(b"keyUsage", True, b"Digital Signature, Non Repudiation, Key Encipherment"),
        crypto.X509Extension(b"extendedKeyUsage", True,
                             b"TLS Web Server Authentication, TLS Web Client Authentication"),
        crypto.X509Extension(b"basicConstraints", True, b"CA:FALSE, pathlen:0")
    ])
    cert.sign(key, 'sha512')
    with open('server.crt', 'wb') as cert_file:
        cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open('server.key', 'wb') as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    save_key_to_keyring(key)
    print('Сертификат и ключ успешно сгенерированы')

class Server:
    def __init__(self):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 443
        self.connections = []
        self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
        self.ssl_context.set_ciphers('ECDHE+AESGCM')
        self.ssl_context.load_cert_chain(certfile='server.crt', keyfile='server.key')
        os.remove('server.key')

    def start(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_ssl = self.ssl_context.wrap_socket(self.s, server_side=True)
        self.s_ssl.bind((self.host, self.port))
        self.s_ssl.listen(2)
        print(f'Server started on {self.host}:{self.port}')

        while True:
            try:
                conn, addr = self.s_ssl.accept()
                self.connections.append(conn)
                threading.Thread(target=self.handle_client, args=(conn,)).start()
            except (ssl.SSLError, ssl.CertificateError) as e:
                continue
    
    def handle_client(self, conn):
        while True:
            try:
                data = conn.recv(1024)
            except ssl.SSLError:
                break
            if data:
                sender = conn.getpeername()
                for client_conn in self.connections:
                    if client_conn != conn:
                        client_conn.sendall((data.decode()).encode())
            else:
                self.connections.remove(conn)
                break
        conn.close()

if __name__ == '__main__':
    server = Server()
    server.start()
