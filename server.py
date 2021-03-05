#!/usr/bin/env python3
import socket
import select
import threading
from datetime import datetime
import logging

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 11234
writing_thread = None
logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{',
    filename='%slog' % __file__[:-2],
    filemode='a'
)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
sockets_list = [server_socket]
clients = {}

print(f'\nPython3 Server started on {socket.gethostname()} at {datetime.now().strftime("%H:%M:%S %b-%d-%Y")}.\n')
print(f'Listening for connections on {IP}:{PORT}...\n\n')


def log_debug(log):
    logging.debug(log)


def log_warning(log):
    logging.warning(log)


def parse_text(data):
    return data


def append_text(username, data):
    print("writing to file in a thread")
    with open(f"rec_data/{username}_data.txt", "a") as file:
        file.write(parse_text(data))


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except Exception:
        return False


try:
    server_socket.listen()
    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                user = receive_message(client_socket)
                if user is False:
                    continue
                sockets_list.append(client_socket)
                clients[client_socket] = user
                username = user['data'].decode('utf-8')
                address = str(client_address).replace('(', '').replace(')', '').replace(',', ':').replace('\'', '')
                msg = f'Accepted new connection from {address}, username: {username}'
                print(msg)
                log_debug(msg)
            else:
                message = receive_message(notified_socket)
                if message is False:
                    username = clients[notified_socket]['data'].decode('utf-8')
                    log = f"Closed connection from: {username}"
                    print(log)
                    log_warning(log)
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue
                user = clients[notified_socket]
                username = user["data"].decode("utf-8")
                msg = message["data"].decode("utf-8")
                if writing_thread!=None:
                    writing_thread.join()
                writing_thread = threading.Thread(target=append_text, args=(username, msg))
                writing_thread.start()
                msg = f'Received message from {username}: {msg}'
                print(msg)
                log_debug(msg)
                for client_socket in clients:
                    if client_socket != notified_socket:
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]
except KeyboardInterrupt:
    for client_socket in sockets_list:
        client_socket.close()
        sockets_list.remove(client_socket)
    server_socket.close()
    print("\nClosing server...")
