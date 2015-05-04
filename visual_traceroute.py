import sys
import urllib3

from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtWebKitWidgets import *
from PyQt5.QtCore import pyqtSlot

from traceroute import TraceRoute
import visual_traceroute_ui


# todo
# - unit testing
# - add "About" box
# - only works with IP4, look at IP6
# - fix up invalid url handling
# - move stuff to config file (commands, google maps key, etc)
# - documentation
# - move html into separate file


map_html = '''
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
    <script>

        var route_details = [];

        try{
            var num_hops = route_list.num_routes();
            var debug = "";
            for(i = 0; i < num_hops;i++){
                debug = debug + route_list.get_ip(i) + " : ";
            }
            alert("From route_list..." + debug);


            for(i = 0; i < num_hops; i++){
                var details = {
                    longitude: route_list.get_longitude(i),
                    latitude: route_list.get_latitude(i),
                    country: route_list.get_country(i),
                    isp: route_list.get_ISP(i),
                    ip: route_list.get_ip(i)
                };
                route_details[route_details.length] = details;
            }
        }catch(e){
            alert(e);
        }


    </script>
    <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&signed_in=true"></script>
    <script language="JavaScript">



   var flightPlanCoordinates = [  ];



function initialize() {
    for(i = 0; i < num_hops; i++){

        var ip = route_details[i].ip;
        var lat = parseFloat(route_details[i].latitude);
        var long = parseFloat(route_details[i].longitude);
        if (i == 0){
            centreLat = lat;
            centreLong = long;
        }
        flightPlanCoordinates[flightPlanCoordinates.length] = new google.maps.LatLng(lat, long);
    }

    alert("flightPlanCoordinates size : " + flightPlanCoordinates.length);

  var mapOptions = {
    zoom: 3,
    center: new google.maps.LatLng(centreLat, centreLong),
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
      var route = route_details[i];
      var mouse_over = route.ip;
      var marker = new google.maps.Marker({
          position: flightPlanCoordinates[i],
          map: map,
          title: mouse_over
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


working_html = '''
<!DOCTYPE html>
<html>
  <head>
  </head>
  <body>
    <div id="map-canvas"></div>
    <font size="4" face="verdana" >Working...</font>
  </body>
</html>'''


class VisualTraceRoute(QMainWindow, visual_traceroute_ui.Ui_visual_traceroute_main_window):
    """ Performs a trace route on a given IP address, and displays
        as a raw text output and an overlay on top of Google Maps.

        This makes use of http://ip-api.com to determine the latitude and longitude (among other
        attributes) of each IP address in the route.
    """
    def __init__(self):
        """
        Sets up the initial windows
        """
        super(VisualTraceRoute, self).__init__()
        self.setupUi(self)
        self.statusbar.show()
        self.setWindowTitle("Visual TraceRoute")
        self.setWindowIcon(QIcon('network-icon.png'))
        self.route_list_wrapper = RouteWrapper()

        # set up buttons
        self.doLookupPushButton.setToolTip("start Trace Route")
        self.doLookupPushButton.clicked.connect(self.handle_do_it_button)
        self.doLookupPushButton.setAutoDefault(True)
        self.closePushButton.setToolTip("Exit application")
        self.closePushButton.clicked.connect(self.close)

        # set up menu handlers
        self.aboutMenuItem.triggered.connect(self.on_about)
        self.exitMenuItem.triggered.connect(self.close)

        # set up async worker thread
        self.traceroute_handler = None

        # set up web view
        hbx = QHBoxLayout()
        self.map.setLayout(hbx)
        self.web = QWebView()
        self.web.page().mainFrame().javaScriptWindowObjectCleared.connect(self.add_JS)
        self.web.page().mainFrame().addToJavaScriptWindowObject("route_list", self.route_list_wrapper)
        hbx.addWidget(self.web)
        self.web.show()


    @pyqtSlot()
    def add_JS(self):
        """ Needed to repopulate the Javascript with the python objects each time the web page is refreshed

        :return: None
        """
        print("**repopulating JS content")
        self.web.page().mainFrame().addToJavaScriptWindowObject("route_list", self.route_list_wrapper)


    @pyqtSlot()
    def handle_do_it_button(self):
        """ Called when the 'DoIt' button is pressed.
            Reads the entered URL, validates it and initiates the trace route command
        :return: None
        """
        try:
            self.statusbar.clearMessage()
            self.statusbar.showMessage("Working...")
            self.doLookupPushButton.setEnabled(False)
            self.textOutput.clear()

            url = self.get_url()

            if url:
                self.web.setHtml(working_html)
                self.traceroute_handler = TraceRoute(url)

                # set up callbacks for the trace route output
                self.traceroute_handler.traceRouteTerminated.connect(self.traceroute_complete)
                self.traceroute_handler.textOutputReady.connect(self.add_results)

                self.traceroute_handler.start()

            else:
                self.statusbar.showMessage("URL is invalid", 5000)
                self.doLookupPushButton.setEnabled(True)

                QMessageBox.information(self, "Empty Field",
                                    "The entered URL is invalid")

        except Exception as e:
            QMessageBox.critical(self,
                                 "Critical",
                                 "Problem initiating trace route : " + str(e))

    @pyqtSlot(str)
    def add_results(self, command_output):
        """
        Accepts a single line of text from the traceroute command, and displays on the text view
        :param command_output: a single line from the traceroute output
        :return: None
        """
        try:
            self.textOutput.moveCursor(QTextCursor.End)
            self.textOutput.insertPlainText(command_output)
        except Exception as e:
            QMessageBox.critical(self,
                                 "Critical",
                                 "Problem updating UI with traceroute text output : " + str(e))

    @pyqtSlot(object)
    def traceroute_complete(self, route_list):
        """
        Called when the trace route command is complete.
        Takes the entire route list, passes it to the Javascript and draws the visual trace route
        :param route_list: a list of IP addresses
        :return: None
        """
        try:
            self.doLookupPushButton.setEnabled(True)
            self.doLookupPushButton.update()
            self.statusbar.clearMessage()
            self.statusbar.showMessage("Complete!")

            self.route_list_wrapper.clear()
            self.route_list_wrapper.add(route_list)
            self.web.page().mainFrame().addToJavaScriptWindowObject("route_list", self.route_list_wrapper)

            self.web.setHtml(map_html)

        except Exception as e:
                QMessageBox.critical(self,
                                 "Critical",
                                 "Problem performing TraceRoute command : " + str(e))

    @pyqtSlot()
    def on_about(self):
        box = QMessageBox.information(self, "About Visual TraceRoute", "Visual trace route")


    def get_url(self):
        """
        Validates the entered URL
        :return: None (if invalid), the url otherwise
        """
        text_url = self.urlLineEdit.text()

        try:
            urllib3.urlopen(text_url)
        except:
            return None

        return text_url


    def closeEvent(self, event):
        """
        Intercepts the app exit event
        :param event: incoming close event
        :return: None
        """
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message',
                                     quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class RouteWrapper(QtCore.QObject):
    """
    A class used for holding attributes that are passed into the QWebView Javascript container
    """
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.routes = []

    def clear(self):
        self.routes = []

    def add(self, route_list):
        self.routes = route_list

    @pyqtSlot(result="int")
    def num_routes(self):
        for r in self.routes:
            print("py route : " + r["query"])
        return len(self.routes)

    @pyqtSlot(int, result=str)
    def get_ip(self, offset):
        row = self.routes[offset]
        return str(row["query"])

    @pyqtSlot(int, result=str)
    def get_longitude(self, offset):
        row = self.routes[offset]
        return str(row["lon"])

    @pyqtSlot(int, result=str)
    def get_latitude(self, offset):
        row = self.routes[offset]
        return str(row["lat"])

    @pyqtSlot(int, result=str)
    def get_ISP(self, offset):
        row = self.routes[offset]
        return str(row["isp"])

    @pyqtSlot(int, result=str)
    def get_country(self, offset):
        row = self.routes[offset]
        return str(row["country"])

    @pyqtSlot(int, result=str)
    def get_timezone(self, offset):
        row = self.routes[offset]
        return str(row["timezone"])




app = QApplication(sys.argv)
nu = VisualTraceRoute()
nu.show()
app.exec_()
