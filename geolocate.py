import socket

from PyQt4 import QtCore
from PyQt4.QtCore import QThread
import requests

from utils import CommandTypes


class GeolocateQuery(QThread):
    '''Class to take an IP address and/or URL, and retrieve goelocate information'''

    def __init__(self, url, ip_addr, process_manager):
        QThread.__init__(self)
        self.url = url
        self.ip_addr = ip_addr
        self.reply = None
        self.process_manager = process_manager

    def run(self):
        self.process_manager.register_process("geolocate")

        try:
            if self.ip_addr is None:
                self.ip_addr = socket.gethostbyname(self.url)

            query_url = 'http://ip-api.com/json/' + self.ip_addr
            self.reply = requests.get(query_url).json()

            if self.reply["status"] != "success":
                self.reply = None

            self.emit(QtCore.SIGNAL(str(CommandTypes.Geolocate)), CommandTypes.Geolocate, self.reply)
        except Exception as e:
            print("Location could not be determined automatically")
        finally:
            self.process_manager.deregister_process("geolocate")
