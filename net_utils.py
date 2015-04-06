import os
import sys

from PyQt4 import QtCore
from PyQt4.QtCore import QUrl, Qt
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from geolocate import GeolocateQuery, GeolocateFields
from traceroute import *

from utils import CommandTypes, WorkerThread, AsynchProcess
import network_utils_ui

# todo
# - add a busy widget to tabs
# - unit testing
# move stuff to config file (commands, google maps key, etc)

class NetUtil(QMainWindow, network_utils_ui.Ui_networkutils):
    def __init__(self):
        super(NetUtil, self).__init__()
        self.setupUi(self)
        self.statusbar.show()
        self.doLookupPushButton.clicked.connect(self.handle_do_it_button)

        hbx = QHBoxLayout()
        self.visualTraceRoute.setLayout(hbx)
        web = QWebView()
        web.load(QUrl("https://www.google.ie"))
        hbx.addWidget(web)
        web.show()


        # set up worker threads for running commands
        self.ping_handler = None
        self.dns_handler = None
        self.nslookup_handler = None
        self.traceroute_handler = None
        self.webserver_handler = None
        self.geolocate_handler = None
        self.traceroute_handler = None

        self.commands_to_run = {
            CommandTypes.Ping: "ping -c 10",
            CommandTypes.TraceRoute: "traceroute",
            CommandTypes.Dig: "dig",
            CommandTypes.nslookup: "nslookup",
            CommandTypes.WebServer: "iiiiiiiii",
            CommandTypes.Geolocate: "unused",

        }


    def perform_ping(self, url):
        ping_command = self.commands_to_run[CommandTypes.Ping] + " " + url
        self.pingTextBrowser.setText("Working...")
        self.ping_handler = AsynchProcess(CommandTypes.Ping, ping_command)
        self.connect(self.ping_handler, QtCore.SIGNAL(str(ping_command)), self.add_results)
        self.ping_handler.start()

    def perform_dns(self, url):
        dig_command = self.commands_to_run[CommandTypes.Dig] + " " + url
        self.dnsTextBrowser.setText("Working...")
        self.dns_handler = WorkerThread(CommandTypes.Dig, dig_command)
        self.connect(self.dns_handler, QtCore.SIGNAL(str(dig_command)), self.add_results)
        self.dns_handler.start()

    def perform_nslookup(self, url):
        nslookup_command = self.commands_to_run[CommandTypes.nslookup] + " " + url
        self.nslookupTextBrowser.setText("Working...")
        self.nslookup_handler = WorkerThread(CommandTypes.nslookup, nslookup_command)
        self.connect(self.nslookup_handler, QtCore.SIGNAL(str(nslookup_command)), self.add_results)
        self.nslookup_handler.start()

    def perform_geolocate(self, url):
        self.geolocateTextBrowser.setText("Working...")
        self.geolocate_handler = GeolocateQuery(url, None)
        self.connect(self.geolocate_handler, QtCore.SIGNAL(str(CommandTypes.Geolocate)), self.add_results)
        self.geolocate_handler.start()

    def perform_traceroute(self, url):
        traceroute_command = self.commands_to_run[CommandTypes.TraceRoute] + " " + url
        self.tracerouteTextBrowser.setText("Working...")
        self.traceroute_handler = WorkerThread(CommandTypes.TraceRoute, traceroute_command)
        self.connect(self.traceroute_handler, QtCore.SIGNAL(str(traceroute_command)), self.add_results)
        self.traceroute_handler.start()

    def handle_do_it_button(self):
        self.statusbar.clearMessage()

        url = self.get_url()
        if url:

            # ping
            self.perform_ping(url)

            # dig
            #self.perform_dns(url)

            # nslookup
            #self.perform_nslookup(url)

            # traceroute
            #self.perform_traceroute(url)

            # geolocate
            #self.perform_geolocate(url)
        else:
            self.statusbar.showMessage("URL is empty", 5000)

    def add_results(self, command_type, command_output):
        if command_type == CommandTypes.Ping:
            self.pingTextBrowser.append(command_output)
        elif command_type == CommandTypes.Dig:
            self.dnsTextBrowser.clear()
            self.dnsTextBrowser.setText(command_output)
        elif command_type == CommandTypes.nslookup:
            self.nslookupTextBrowser.clear()
            self.nslookupTextBrowser.setText(command_output)
        elif command_type == CommandTypes.Geolocate:
            self.geolocateTextBrowser.clear()
            disp = ""
            disp = disp + "Latitude      : " + str(self.geolocate_handler.get_field(GeolocateFields.Latitude)) + os.linesep
            disp = disp + "Longitude     : " + str(self.geolocate_handler.get_field(GeolocateFields.Longitude)) + os.linesep
            disp = disp + "ASName        : " + str(self.geolocate_handler.get_field(GeolocateFields.ASNumberName)) + os.linesep
            disp = disp + "ISP           : " + self.geolocate_handler.get_field(GeolocateFields.ISP) + os.linesep
            disp = disp + "City          : " + self.geolocate_handler.get_field(GeolocateFields.City) + os.linesep
            disp = disp + "RegionName    : " + self.geolocate_handler.get_field(GeolocateFields.RegionName) + os.linesep
            disp = disp + "Region        : " + self.geolocate_handler.get_field(GeolocateFields.Region) + os.linesep
            disp = disp + "Country       : " + self.geolocate_handler.get_field(GeolocateFields.Country) + os.linesep
            disp = disp + "Country Code  : " + self.geolocate_handler.get_field(GeolocateFields.CountryCode) + os.linesep
            disp = disp + "Timezone      : " + self.geolocate_handler.get_field(GeolocateFields.Timezone) + os.linesep
            self.geolocateTextBrowser.setText(disp)
        elif command_type == CommandTypes.TraceRoute:
            self.handle_trace_route(command_output)

    def handle_trace_route(self, output):
        self.tracerouteTextBrowser.clear()
        self.tracerouteTextBrowser.setText(output)


        # now update the


        cleaned_up = parse_traceroute_output(output)

        route = ""
        i = 1
        for hop in cleaned_up:
            route = route + str(i) + " : " + hop + os.linesep
            i += 1
        self.tracerouteTextBrowser.setText(route)


    def get_url(self):
        # todo - validate url input and prompt dialog
        return self.urlLineEdit.text()


app = QApplication(sys.argv)
nu = NetUtil()
nu.show()
app.exec_()
