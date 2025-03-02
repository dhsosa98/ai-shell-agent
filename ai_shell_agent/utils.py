import sys
import time
import threading
from colorama import Fore, Style

class Spinner:
    def __init__(self, message="Thinking", delay=0.1):
        self.spinner = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        self.delay = delay
        self.busy = False
        self.spinner_visible = False
        self.message = message
        self.sys_write_lock = threading.Lock()

    def write_next(self):
        with self.sys_write_lock:
            if not self.spinner_visible:
                sys.stdout.write(f'\r{Fore.CYAN}{self.message} {self.spinner[self.spinner_index]}{Style.RESET_ALL} ')
                sys.stdout.flush()
                self.spinner_index = (self.spinner_index + 1) % len(self.spinner)
                self.spinner_visible = True

    def remove_spinner(self, cleanup=False):
        with self.sys_write_lock:
            if self.spinner_visible:
                sys.stdout.write('\r')
                sys.stdout.write(' ' * (len(self.message) + 10))  # Extra space to ensure full erasure
                sys.stdout.write('\r')
                sys.stdout.flush()
                self.spinner_visible = False
                if cleanup:
                    sys.stdout.write(Style.RESET_ALL)

    def spinner_task(self):
        while self.busy:
            self.write_next()
            time.sleep(self.delay)
            self.remove_spinner()

    def __enter__(self):
        self._screen_lock = threading.Lock()
        self.busy = True
        self.spinner_index = 0
        self.spinner_visible = False
        self.thread = threading.Thread(target=self.spinner_task)
        self.thread.daemon = True
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.busy = False
        time.sleep(self.delay * 2)  # Give more time to clean up
        self.remove_spinner(cleanup=True)
        sys.stdout.flush()  # Ensure output is flushed 