import sys

from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import simplejson as json
from traceroute import TraceRoute

from geolocate import GeolocateQuery
import visual_traceroute_ui


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



html1 = '''
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

html = '''
<html><body>
  <center>
  <script language="JavaScript">
    var a = route_list.route();
    document.write('<p>route_list ' + a[1] + '</p>')
  </script>
 </center>
</body></html>
'''


class VisualTraceRoute(QMainWindow, visual_traceroute_ui.Ui_visual_traceroute_main_window):
    def __init__(self):
        super(VisualTraceRoute, self).__init__()
        self.setupUi(self)
        self.statusbar.show()

        # set up buttons
        self.doLookupPushButton.clicked.connect(self.handle_do_it_button)
        self.closePushButton.clicked.connect(app.exit)

        # set up async worker thread
        self.traceroute_handler = None

        # self.connect(self, QtCore.SIGNAL("traceroute_line"), self.add_results)
        # self.connect(self, QtCore.SIGNAL("traceroute_complete"), self.traceroute_complete)



    def handle_do_it_button(self):
        try:
            self.draw_visual_trace_route([])

            # self.statusbar.clearMessage()
            # self.statusbar.showMessage("Working...")
            # self.doLookupPushButton.setEnabled(False)
            #
            # url = self.get_url()
            #
            # url="www.rte.ie"
            # if url:
            #     # traceroute
            #     self.perform_traceroute(url)
            # else:
            #     self.statusbar.showMessage("URL is empty", 5000)
            #     self.doLookupPushButton.setEnabled(True)


        except Exception as e:
            QMessageBox.critical(self,
                         "Critical",
                         "Problem performing network lookup : " + str(e))


    def add_results(self, command_output):
        try:
            self.textOutput.moveCursor(QTextCursor.End)
            self.textOutput.insertPlainText(command_output)
        except Exception as e:
            QMessageBox.critical(self,
                         "Critical",
                         "Problem updating UI with traceroute text output : " + str(e))



    def traceroute_complete(self, route_list):
        self.doLookupPushButton.setEnabled(True)
        self.doLookupPushButton.update()
        self.statusbar.clearMessage()
        self.statusbar.showMessage("Complete!")

        print(route_list)
        self.draw_visual_trace_route(route_list)



    def draw_visual_trace_route(self, route_list):
        # set up for visual traceroute
        hbx = QHBoxLayout()
        self.map.setLayout(hbx)
        web = QWebView()
        route_wrapper = RouteWrapper(route_list)
        web.page().mainFrame().addToJavaScriptWindowObject("route_list", route_wrapper)
        web.setHtml(html)
        hbx.addWidget(web)
        web.show()


    def perform_traceroute(self, url):
        try:
            self.traceroute_handler = TraceRoute(url)
            #self.connect(self.traceroute_handler, QtCore.SIGNAL("process_terminated"), self.traceroute_complete)
            self.connect(self.traceroute_handler, QtCore.SIGNAL("traceroute_line"), self.add_results)
            self.connect(self.traceroute_handler, QtCore.SIGNAL("traceroute_complete"), self.traceroute_complete)

            self.traceroute_handler.start()
        except Exception as e:
            QMessageBox.critical(self,
                                 "Critical",
                                 "Problem performing TraceRoute command : " + str(e))

    def get_url(self):
        # todo - validate url input and prompt dialog
        return self.urlLineEdit.text()


class RouteWrapper(QtCore.QObject):
    def __init__(self, route_list):
        QtCore.QObject.__init__(self)
        self.routes = route_list
        self.routes.append("qwe")
        self.routes.append("aaa")
        self.routes.append("ddd")
        self.routes.append("rrr")


        print("in RouteWrapper init....routes = " + str(self.routes))

    @QtCore.pyqtSlot(result="int")
    def constant_one(self):
        return 1;

    @QtCore.pyqtSlot(result=QtCore.QVariant)
    def route(self):
        return self.routes

    def size(self):
        return len(self.route_list)

    @QtCore.pyqtSlot(result=str)
    def msg(self):
        return "hello"

app = QApplication(sys.argv)
nu = VisualTraceRoute()
nu.show()
app.exec_()
