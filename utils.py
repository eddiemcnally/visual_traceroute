from enum import Enum
import subprocess
import queue
import time

from PyQt4 import QtCore
from PyQt4 import QtGui
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


class ProcessManager(QObject):
    ''' A class that keeps track of the running processes '''

    def __init__(self):
        QObject.__init__(self)
        self.process_list = []
        self.signal_name = "all_processes_terminated"
        # self.connect(self.thread(), QtCore.SIGNAL("registerProcess()"), self.register_process)
        #self.connect(self.thread(), QtCore.SIGNAL("deregisterProcess()"), self.deregister_process)
        self.lock_obj = QtCore.QMutex()

    def register_process(self, process):
        try:
            self.lock_obj.lock()
            self.process_list.append(process)
        finally:
            self.lock_obj.unlock()

    def deregister_process(self, process):
        try:
            self.lock_obj.lock()
            self.process_list.remove(process)
            if len(self.process_list) == 0:
                self.emit(QtCore.SIGNAL(self.signal_name))
        finally:
            self.lock_obj.unlock()


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
        try:
            for line in iter(self._fd.readline, ''):
                st_line = line.decode("utf-8")
                if st_line:
                    self._queue.put(st_line)
        except:
            pass


class AsynchProcess(QtCore.QThread):
    '''Main asynch class: uses subprocess to execute the command, polls the stdout queue and fires
    signals'''

    def __init__(self, command_type, command, process_manager):
        QThread.__init__(self)
        self.command = command
        self.command_type = command_type
        self.process_manager = process_manager

    def run(self):
        try:
            self.process_manager.register_process(str(self.command))

            process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            # Launch the asynchronous readers of the process' stdout.
            stdout_queue = queue.Queue()
            stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
            stdout_reader.start()

            while True:
                time.sleep(.2)
                if process.poll() is not None and stdout_queue.empty():
                    break

                # Show what we received from standard output.
                while not stdout_queue.empty():
                    line = stdout_queue.get()
                    self.emit(QtCore.SIGNAL(str(self.command)), self.command_type, line)

            # cleanup
            stdout_reader.terminate()
            process.stdout.close()

        except Exception as e:
            QtGui.QMessageBox.critical(self,
                                       "Critical",
                                       "Problem performing command....command='" + self.command + "' error = " + str(e))

        finally:
            self.process_manager.deregister_process(str(self.command))


