import sys

from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKitWidgets import *

from PyQt5.QtCore import pyqtSignal, pyqtSlot

from traceroute import TraceRoute
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
            alert("%R%R%R%R%R%R"  + e);
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

enter_url_html = '''
<!DOCTYPE html>
<html>
  <head>
  </head>
  <body>
    <div id="map-canvas"></div>
    <p>Enter a URl to continue...</p>
  </body>
</html>'''

working_html = '''
<!DOCTYPE html>
<html>
  <head>
  </head>
  <body>
    <div id="map-canvas"></div>
    <p>Working...</p>
  </body>
</html>'''



class VisualTraceRoute(QMainWindow, visual_traceroute_ui.Ui_visual_traceroute_main_window):
    def __init__(self):
        super(VisualTraceRoute, self).__init__()
        self.setupUi(self)
        self.statusbar.show()
        self.route_list_wrapper = RouteWrapper()

        # set up buttons
        self.doLookupPushButton.clicked.connect(self.handle_do_it_button)
        self.closePushButton.clicked.connect(app.exit)

        # set up async worker thread
        self.traceroute_handler = None

        # set up web view
        hbx = QHBoxLayout()
        self.map.setLayout(hbx)
        self.web = QWebView()
        self.web.page().mainFrame().javaScriptWindowObjectCleared.connect(self.add_JS)
        #self.web.page().mainFrame().addToJavaScriptWindowObject("route_list", self.route_list_wrapper)
        self.web.setHtml(map_html)
        hbx.addWidget(self.web)
        self.web.show()


    @pyqtSlot()
    def add_JS(self):
        print("**repopulating JS content")
        self.web.page().mainFrame().addToJavaScriptWindowObject("route_list", self.route_list_wrapper)


    @pyqtSlot()
    def handle_do_it_button(self):
        try:
            self.statusbar.clearMessage()
            self.statusbar.showMessage("Working...")
            self.doLookupPushButton.setEnabled(False)
            self.textOutput.clear()

            url = self.get_url()

            url = "www.microsoft.com";
            if url:
                self.display_empty_visual_route_pane(working_html)
                self.perform_traceroute(url)
            else:
                self.statusbar.showMessage("URL is empty", 5000)
                self.doLookupPushButton.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self,
                         "Critical",
                         "Problem performing network lookup : " + str(e))

    @pyqtSlot(str)
    def add_results(self, command_output):
        try:
            self.textOutput.moveCursor(QTextCursor.End)
            self.textOutput.insertPlainText(command_output)
        except Exception as e:
            QMessageBox.critical(self,
                         "Critical",
                         "Problem updating UI with traceroute text output : " + str(e))

    @pyqtSlot(object)
    def traceroute_complete(self, route_list):

        try:
            # with open('/home/eddie/dev/projects/python/visual_traceroute/test/test_route_data', 'wb') as f:
            #      pickle.dump(route_list, f)

            self.doLookupPushButton.setEnabled(True)
            self.doLookupPushButton.update()
            self.statusbar.clearMessage()
            self.statusbar.showMessage("Complete!")

            print(route_list)
            self.draw_visual_trace_route(route_list)

        except Exception as e:
                QMessageBox.critical(self,
                         "Critical",
                         "Problem updating UI with traceroute text output : " + str(e))


    def draw_visual_trace_route(self, route_list):
        try:
            self.route_list_wrapper.clear()
            self.route_list_wrapper.add(route_list)
            #self.web.setHtml(map_html)

            print("***setting up JS object...")
        except Exception as e:
            QMessageBox.critical(self,
                                 "Critical",
                                 "*****Problem performing TraceRoute command : " + str(e))



    def display_empty_visual_route_pane(self, html):
        #self.web.setHtml(html)
        pass

    def perform_traceroute(self, url):
        try:
            self.traceroute_handler = TraceRoute(url)

            self.traceroute_handler.traceRouteTerminated.connect(self.traceroute_complete)
            self.traceroute_handler.textOutputReady.connect(self.add_results)

            self.traceroute_handler.start()
        except Exception as e:
            QMessageBox.critical(self,
                                 "Critical",
                                 "Problem performing TraceRoute command : " + str(e))

    def get_url(self):
        # todo - validate url input and prompt dialog
        return self.urlLineEdit.text()



class RouteWrapper(QtCore.QObject):
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
            print ("py route : " + r["query"])
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
