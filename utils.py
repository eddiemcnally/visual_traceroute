from enum import Enum
import subprocess
import queue
import time
from PyQt4 import QtCore
from PyQt4.QtCore import *


class CommandTypes(Enum):
    '''Commands being run'''
    Dig = 1
    TraceRoute = 2
    nslookup = 3
    WebServer = 4
    Geolocate = 5
    Whois = 6
    Ping = 7


class AsynchronousFileReader(QtCore.QThread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    '''

    def __init__(self, fd, queue):
        assert callable(fd.readline)
        QThread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        '''The body of the thread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            st_line = line.decode("utf-8")
            if st_line:
                self._queue.put(st_line)
            #time.sleep(.1)


class AsynchProcess(QtCore.QThread):
    '''Main asynch class: uses subprocess to execute the command, polls the stdout queue and fires
    signals'''

    def __init__(self, command_type, command):
        QThread.__init__(self)
        self.command = command
        self.command_type = command_type


    def run(self):
        '''
        Example of how to consume standard output and standard error of
        a subprocess asynchronously without risk on deadlocking.
        '''
        process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        # Launch the asynchronous readers of the process' stdout.
        stdout_queue = queue.Queue()
        stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
        stdout_reader.start()

        while True:
            time.sleep(.2)

            # Show what we received from standard output.
            while not stdout_queue.empty():
                line = stdout_queue.get()
                self.emit(QtCore.SIGNAL(str(self.command)), self.command_type, line)

            if process.poll() is not None and stdout_queue.empty() and not stdout_reader.isRunning():
                break

        # cleanup
        stdout_reader.terminate()
        process.stdout.close()
