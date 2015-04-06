from PyQt4 import QtCore
from enum import Enum
import socket
from PyQt4.QtCore import QThread
import requests
from utils import CommandTypes


class GeolocateQuery(QThread):
    def __init__(self, url, ip_addr):
        QThread.__init__(self)
        self.url = url
        self.ip_addr = ip_addr
        self.reply = None

    def run(self):
        if self.ip_addr is None:
            self.ip_addr = socket.gethostbyname(self.url)

        try:
            query_url = 'http://ip-api.com/json/' + self.ip_addr
            self.reply = requests.get(query_url).json()

            if self.reply["status"] != "success":
                self.reply = None

            self.emit(QtCore.SIGNAL(str(CommandTypes.Geolocate)), CommandTypes.Geolocate, self.reply)

        except Exception as e:
            print("Location could not be determined automatically")

    def dump_data(self):
        return self.reply

    def get_field(self, geolocateFieldEnum):
        if self.reply is None:
            return None

        if geolocateFieldEnum == GeolocateFields.ASNumberName:
            return self.reply["as"]
        elif geolocateFieldEnum == GeolocateFields.Country:
            return self.reply["country"]
        elif geolocateFieldEnum == GeolocateFields.CountryCode:
            return self.reply["countryCode"]
        elif geolocateFieldEnum == GeolocateFields.Region:
            return self.reply["region"]
        elif geolocateFieldEnum == GeolocateFields.RegionName:
            return self.reply["regionName"]
        elif geolocateFieldEnum == GeolocateFields.City:
            return self.reply["city"]
        elif geolocateFieldEnum == GeolocateFields.Latitude:
            return self.reply["lat"]
        elif geolocateFieldEnum == GeolocateFields.Longitude:
            return self.reply["lon"]
        elif geolocateFieldEnum == GeolocateFields.Timezone:
            return self.reply["timezone"]
        elif geolocateFieldEnum == GeolocateFields.ISP:
            return self.reply["isp"]
        elif geolocateFieldEnum == GeolocateFields.Org:
            return self.reply["org"]
        else:
            return None


class GeolocateFields(Enum):
    Status = 1
    Country = 2
    CountryCode = 3
    Region = 4
    RegionName = 5
    City = 6
    Latitude = 7
    Longitude = 8
    Timezone = 9
    ISP = 10
    Org = 11
    ASNumberName = 12
