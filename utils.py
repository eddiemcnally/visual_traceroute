from enum import Enum
import subprocess
import queue
import time
from PyQt4 import QtCore
from PyQt4.QtCore import *


class CommandTypes(Enum):
    Dig = 1
    TraceRoute = 2
    nslookup = 3
    WebServer = 4
    Geolocate = 5
    Whois = 6
    Ping = 7


class WorkerThread(QtCore.QThread):

    def __init__(self, command_type, command):
        QThread.__init__(self)
        self.command = command
        self.command_type = command_type

    def run(self):
        p = subprocess.Popen(self.command, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()

        # Wait to terminate. Get return return code #
        p_status = p.wait()

        try:
            if p_status != 0:
                err_str = "Problem running command " + self.command + ", output : " + str(output) + " status: " + str(p_status) + " err : " + str(err)
                self.emit(QtCore.SIGNAL(str(self.command)), self.command_type, err_str)
            else:
                self.emit(QtCore.SIGNAL(str(self.command)), self.command_type, output.decode("utf-8"))
        except Exception as e:
            print("Location could not be determined automatically " + e)

        return

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
        '''The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            st_line = line.decode("utf-8")
            print("st_line len = " + str(len(st_line)))
            if st_line:
                print("Writing line '" + st_line + "'")
                self._queue.put(st_line)
            time.sleep(1)

    def eof(self):
        '''Check whether there is no more content to expect.'''
        return not self.isRunning() and self._queue.empty()


class AsynchProcess(QtCore.QThread):
    def __init__(self, command_type, command):
        QThread.__init__(self)
        self.command = command
        self.command_type = command_type


    def run(self):
        '''
        Example of how to consume standard output and standard error of
        a subprocess asynchronously without risk on deadlocking.
        '''

        # Launch the command as subprocess.
        process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        # Launch the asynchronous readers of the process' stdout and stderr.
        stdout_queue = queue.Queue()
        stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
        stdout_reader.start()
        #stderr_queue = queue.Queue()
        #stderr_reader = AsynchronousFileReader(process.stderr, stderr_queue)
        #stderr_reader.start()


        # Check the queues if we received some output (until there is nothing more to get).
        #stderr_EOF = stderr_reader.eof()

        while not stdout_reader.eof():
            # Show what we received from standard output.
            while not stdout_queue.empty():
                line = stdout_queue.get()
                self.emit(QtCore.SIGNAL(str(self.command)), self.command_type, line)

            # # Show what we received from standard error.
            # while not stderr_queue.empty():
            #     line = stderr_queue.get()
            #     self.emit(QtCore.SIGNAL(str(self.command)), self.command_type, line.decode("utf-8"))

            # Sleep a bit before asking the readers again.
            time.sleep(.1)

        # Let's be tidy and join the threads we've started.
        stdout_reader.join()
        #stderr_reader.join()

        # Close subprocess' file descriptors.
        process.stdout.close()
        #process.stderr.close()
