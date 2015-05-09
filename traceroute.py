import subprocess
import queue
import time

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread

from geolocate import GeolocateQuery


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
    """
    Threaded trace route command handler.
    Issues a trace route command and parses the text output.
    """

    textOutputReady = QtCore.pyqtSignal(str)
    traceRouteTerminated = QtCore.pyqtSignal(object)

    def __init__(self, ip_address):
        assert len(ip_address) >= 8

        QThread.__init__(self)
        self.ip_address = ip_address
        self.retval = []
        self.traceRouteUtils = TraceRouteUtils()

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

                    self.textOutputReady.emit(str(line))

                    # this line has a route
                    ip_addr = self.traceRouteUtils.extract_ip_address(line)
                    if ip_addr is not None:
                        # geolocate the ip address
                        geolocate = GeolocateQuery(ip_addr)
                        geo_info = geolocate.do_lookup()
                        if geo_info is not None:
                            self.retval.append(geo_info)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self,
                                           "Critical",
                                           "Problem initiating trace route : " + str(e))
        finally:
            self.traceRouteTerminated.emit(self.retval)


class TraceRouteUtils:
    '''
    Parses the line of output text and extracts an ip address (if one exists)
    '''

    def extract_ip_address(self, line):
        line = line.strip()

        if line[:1] in '0123456789':
            if "* * *" not in line:
                # line has a valid route IP
                if ')' in line and '(' in line:
                    # find IP address and save it
                    start_idx = line.index('(')
                    end_idx = line.index(')')
                    ip_addr = line[start_idx + 1:end_idx]
                    return ip_addr
        return None
