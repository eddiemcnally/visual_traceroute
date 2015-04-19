import sys

from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import simplejson as json

from geolocate import GeolocateQuery
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



html = '''
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>Simple markers</title>
    <style>
      html, body, #map-canvas {
        height: 100%;
        margin: 0px;
        padding: 0px
      }
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&signed_in=true"></script>
    <script>

  var flightPlanCoordinates = [
    new google.maps.LatLng(37.772323, -122.214897),
    new google.maps.LatLng(21.291982, -157.821856),
    new google.maps.LatLng(-18.142599, 178.431),
    new google.maps.LatLng(-27.46758, 153.027892)
  ];

function initialize() {
  var mapOptions = {
    zoom: 3,
    center: new google.maps.LatLng(0, -180),
    mapTypeId: google.maps.MapTypeId.TERRAIN
  };

  var map = new google.maps.Map(document.getElementById('map-canvas'),
      mapOptions);

  var flightPath = new google.maps.Polyline({
    path: flightPlanCoordinates,
    geodesic: true,
    strokeColor: '#FF0000',
    strokeOpacity: 1.0,
    strokeWeight: 2
  });

  flightPath.setMap(map);

  for (i = 0; i < flightPlanCoordinates.length; i++) {
      var marker = new google.maps.Marker({
          position: flightPlanCoordinates[i],
          map: map,
          title: 'Hello World!'
      });
  }
}

google.maps.event.addDomListener(window, 'load', initialize);
    </script>
  </head>
  <body>
    <div id="map-canvas"></div>
  </body>
</html>
'''




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
        self.visualTraceRouteWidget.setLayout(hbx)
        web = QWebView()
        web.setHtml(html)
        hbx.addWidget(web)
        web.show()

        self.updaterMutex = QtCore.QMutex()

        # set up worker threads for running commands
        self.ping_handler = None
        self.dns_handler = None
        self.nslookup_handler = None
        self.traceroute_handler = None
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
        self.connect(self.process_manager, QtCore.SIGNAL(self.process_manager.signal_name),
                     self.all_processes_terminated)

    def perform_ping(self, url):
        try:
            ping_command = self.commands_to_run[CommandTypes.Ping] + " " + url
            self.ping_handler = AsynchProcess(CommandTypes.Ping, ping_command, self.process_manager)
            self.connect(self.ping_handler, QtCore.SIGNAL(str(ping_command)), self.add_results)
            self.ping_handler.start()
        except Exception as e:
            QMessageBox.critical(self,
                                 "Critical",
                                 "Problem performing 'ping' command : " + str(e))

    def perform_dns(self, url):
        try:
            dig_command = self.commands_to_run[CommandTypes.Dig] + " " + url
            self.dns_handler = AsynchProcess(CommandTypes.Dig, dig_command, self.process_manager)
            self.connect(self.dns_handler, QtCore.SIGNAL(str(dig_command)), self.add_results)
            self.dns_handler.start()
        except Exception as e:
            QMessageBox.critical(self,
                                 "Critical",
                                 "Problem performing dns command : " + str(e))

    def perform_nslookup(self, url):
        try:
            nslookup_command = self.commands_to_run[CommandTypes.nslookup] + " " + url
            self.nslookup_handler = AsynchProcess(CommandTypes.nslookup, nslookup_command, self.process_manager)
            self.connect(self.nslookup_handler, QtCore.SIGNAL(str(nslookup_command)), self.add_results)
            self.nslookup_handler.start()
        except Exception as e:
            QMessageBox.critical(self,
                                 "Critical",
                                 "Problem performing nslookup command : " + str(e))

    def perform_geolocate(self, url):
        try:
            self.geolocate_handler = GeolocateQuery(url, None, self.process_manager)
            self.connect(self.geolocate_handler, QtCore.SIGNAL(str(CommandTypes.Geolocate)), self.add_results)
            self.geolocate_handler.start()
        except Exception as e:
            QMessageBox.critical(self,
                                 "Critical",
                                 "Problem doing geolocate : " + str(e))

    def handle_do_it_button(self):
        try:
            self.statusbar.clearMessage()
            self.statusbar.showMessage("Working...")
            self.doLookupPushButton.setEnabled(False)

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

        except Exception as e:
            QMessageBox.critical(self,
                         "Critical",
                         "Problem performing network lookup : " + str(e))


    def all_processes_terminated(self):
        self.doLookupPushButton.setEnabled(True)
        self.doLookupPushButton.update()
        self.statusbar.clearMessage()
        self.statusbar.showMessage("Complete!")


    def add_results(self, command_type, command_output):
        try:
            self.updaterMutex.lock()

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
                text = json.dumps(command_output, sort_keys=True, indent=4)
                self.geolocateTextBrowser.moveCursor(QTextCursor.End)
                self.geolocateTextBrowser.insertPlainText(str(text))

        except Exception as e:
            QMessageBox.critical(self,
                                 "Critical",
                                 "Problem updating UI with command output : " + str(e))
        finally:
            self.updaterMutex.unlock()


#def handle_trace_route(self, output):


# self.tracerouteTextBrowser.moveCursor(QTextCursor.End)
#self.tracerouteTextBrowser.insertPlainText(str(output))

#
# # print out IP address
# if (output.index("(")):
#     try:
#         start_ip = output.index("(") - 1
#         end_ip = output.index(")")
#
#         ip_addr = output[start_ip:end_ip]
#         print("IP = " + ip_addr)
#     except Exception as e:
#         QMessageBox.critical(self,
#                          "Critical",
#                          "Problem parsing IP address : " + str(e))

# parse line for IP addresses,and save for later
# cleaned_up = parse_traceroute_output(output)

# route = ""
# i = 1
# for hop in cleaned_up:
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
