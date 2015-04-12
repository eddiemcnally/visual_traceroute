import os
import sys

from PyQt4 import QtCore
from PyQt4.QtCore import QUrl
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

from geolocate import GeolocateQuery, GeolocateFields
from utils import ProcessManager
from utils import CommandTypes, AsynchProcess
import network_utils_ui


# todo
# - unit testing
# - migrate to Qt5
# - only works with IP4, look at IP6
# - fix up invalid url handling
# - move stuff to config file (commands, google maps key, etc)
# - documentation
# - async handling of stderr (same as stdout)
# - add "are you sure" to the close button
# - fix up traceroute output parsing


class NetUtil(QMainWindow, network_utils_ui.Ui_networkutils):
    def __init__(self):
        super(NetUtil, self).__init__()
        self.setupUi(self)
        self.statusbar.show()


        # set up buttons
        self.doLookupPushButton.clicked.connect(self.handle_do_it_button)
        self.closePushButton.clicked.connect(app.exit)

        # set up for visual traceroute
        hbx = QHBoxLayout()
        self.visualTraceRoute.setLayout(hbx)
        web = QWebView()
        web.load(QUrl("https://www.google.ie"))
        hbx.addWidget(web)
        web.show()

        self.updaterMutex = QtCore.QMutex()

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
            CommandTypes.Geolocate: "unused",
        }

        # set up some process management
        self.process_manager = ProcessManager()
        self.connect(self.thread(), QtCore.SIGNAL(self.process_manager.signal_name), self.all_processes_terminated)
        pass

    def perform_ping(self, url):
        try:
            ping_command = self.commands_to_run[CommandTypes.Ping] + " " + url
            self.ping_handler = AsynchProcess(CommandTypes.Ping, ping_command, self.process_manager)
            self.connect(self.ping_handler, QtCore.SIGNAL(str(ping_command)), self.add_results)
            self.ping_handler.start()
        except:
            pass

    def perform_dns(self, url):
        try:
            dig_command = self.commands_to_run[CommandTypes.Dig] + " " + url
            self.dns_handler = AsynchProcess(CommandTypes.Dig, dig_command, self.process_manager)
            self.connect(self.dns_handler, QtCore.SIGNAL(str(dig_command)), self.add_results)
            self.dns_handler.start()
        except:
            pass

    def perform_nslookup(self, url):
        try:
            nslookup_command = self.commands_to_run[CommandTypes.nslookup] + " " + url
            self.nslookup_handler = AsynchProcess(CommandTypes.nslookup, nslookup_command, self.process_manager)
            self.connect(self.nslookup_handler, QtCore.SIGNAL(str(nslookup_command)), self.add_results)
            self.nslookup_handler.start()
        except:
            pass

    def perform_geolocate(self, url):
        try:
            self.geolocate_handler = GeolocateQuery(url, None)
            self.connect(self.geolocate_handler, QtCore.SIGNAL(str(CommandTypes.Geolocate)), self.add_results)
            self.geolocate_handler.start()
        except:
            pass

    def perform_traceroute(self, url):
        traceroute_command = self.commands_to_run[CommandTypes.TraceRoute] + " " + url
        self.traceroute_handler = AsynchProcess(CommandTypes.TraceRoute, traceroute_command)
        self.connect(self.traceroute_handler, QtCore.SIGNAL(str(traceroute_command)), self.add_results)
        self.traceroute_handler.start()

    def handle_do_it_button(self):
        try:
            self.updaterMutex.lock()

            self.statusbar.clearMessage()
            self.statusbar.showMessage("Working...")
            self.doLookupPushButton.setEnabled(False)

            url = self.get_url()
            if url:

                # ping
                self.perform_ping(url)

                # dig
                self.perform_dns(url)

                # nslookup
                self.perform_nslookup(url)

                # traceroute
                # self.perform_traceroute(url)

                # geolocate
                self.perform_geolocate(url)
            else:
                self.statusbar.showMessage("URL is empty", 5000)
        except Exception as e:
            print("Problem doing network ops : " + e)
        finally:
            self.updaterMutex.unlock()


    def all_processes_terminated(self):
        print("start - in all_processes_terminated()")
        self.doLookupPushButton.setEnabled(True)
        self.doLookupPushButton.update()
        self.statusbar.clearMessage()
        self.statusbar.showMessage("Complete!")
        print("end - in all_processes_terminated()")


    def add_results(self, command_type, command_output):
        try:
            if command_type == CommandTypes.Ping:
                self.pingTextBrowser.moveCursor(QTextCursor.End)
                self.pingTextBrowser.insertPlainText(command_output)
            elif command_type == CommandTypes.Dig:
                self.dnsTextBrowser.moveCursor(QTextCursor.End)
                self.dnsTextBrowser.insertPlainText(command_output)
            elif command_type == CommandTypes.nslookup:
                self.nslookupTextBrowser.moveCursor(QTextCursor.End)
                self.nslookupTextBrowser.insertPlainText(command_output)
            elif command_type == CommandTypes.Geolocate:
                self.geolocateTextBrowser.clear()
                disp = ""
                disp = disp + "Latitude      : " + str(
                    self.geolocate_handler.get_field(GeolocateFields.Latitude)) + os.linesep
                disp = disp + "Longitude     : " + str(
                    self.geolocate_handler.get_field(GeolocateFields.Longitude)) + os.linesep
                disp = disp + "ASName        : " + str(
                    self.geolocate_handler.get_field(GeolocateFields.ASNumberName)) + os.linesep
                disp = disp + "ISP           : " + self.geolocate_handler.get_field(GeolocateFields.ISP) + os.linesep
                disp = disp + "City          : " + self.geolocate_handler.get_field(GeolocateFields.City) + os.linesep
                disp = disp + "RegionName    : " + self.geolocate_handler.get_field(
                    GeolocateFields.RegionName) + os.linesep
                disp = disp + "Region        : " + self.geolocate_handler.get_field(GeolocateFields.Region) + os.linesep
                disp = disp + "Country       : " + self.geolocate_handler.get_field(
                    GeolocateFields.Country) + os.linesep
                disp = disp + "Country Code  : " + self.geolocate_handler.get_field(
                    GeolocateFields.CountryCode) + os.linesep
                disp = disp + "Timezone      : " + self.geolocate_handler.get_field(
                    GeolocateFields.Timezone) + os.linesep
                self.geolocateTextBrowser.setText(disp)
            elif command_type == CommandTypes.TraceRoute:
                self.handle_trace_route(command_output)
        except:
            pass

    def handle_trace_route(self, output):
        self.tracerouteTextBrowser.moveCursor(QTextCursor.End)
        self.tracerouteTextBrowser.insertPlainText(output)

        # parse line for IP addresses,and save for later
        # cleaned_up = parse_traceroute_output(output)

        #route = ""
        #i = 1
        #for hop in cleaned_up:
        #route = route + str(i) + " : " + hop + os.linesep
        #i += 1
        #self.tracerouteTextBrowser.setText(route)


    def get_url(self):
        # todo - validate url input and prompt dialog
        return self.urlLineEdit.text()


app = QApplication(sys.argv)
nu = NetUtil()
nu.show()
app.exec_()
