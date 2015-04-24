from enum import Enum
import subprocess
import queue
import time
from geolocate import GeolocateQuery

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import *


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


class TraceRoute(QtCore.QThread):
    def __init__(self, ip_address):
        QThread.__init__(self)
        self.ip_address = ip_address
        self.retval = []


    def run(self):
        try:
            command = "traceroute " + self.ip_address
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

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

                    line = line.strip()

                    if line[:1] in '0123456789':
                        # this line has a route
                        if "*" not in line:
                            # line has a valid route IP
                            if ')' in line and '(' in line:
                                # find IP address and save it
                                start_idx = line.index('(')
                                end_idx = line.index(')')
                                ip_addr = line[start_idx + 1:end_idx]

                                # geolocate the ip address
                                geolocate = GeolocateQuery(ip_addr)
                                geo_info = geolocate.do_lookup()
                                self.retval.append()

            self.emit(QtCore.SIGNAL("process_terminated"),self.retval)

        except Exception as e:
            QtGui.QMessageBox.critical(self,
                                       "Critical",
                                       "Problem performing TraceRoute: Error = " + str(e))

        finally:
            self.emit(QtCore.SIGNAL("process_terminated"),self.retval)


