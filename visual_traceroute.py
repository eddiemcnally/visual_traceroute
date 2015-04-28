import sys

import pickle

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
            alert(e);
        }


    </script>
    <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&signed_in=true"></script>
    <script language="JavaScript">



   var flightPlanCoordinates = [  ];



function initialize() {
    for(i = 0; i < num_hops; i++){
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

html = '''
<html><body>
  <center>
  <script language="JavaScript">
    var a = route_list.size();
    document.write('<p>size = ' + a + '</p>')
    for (i = 0; i < a; i++) {
        document.write('<p>in for loop...i=' + i + '</p>')
        var l = route_list.get_longitude(i);
        document.write('<p>longitude = ' + l + '</p>')
    }

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

            # ---------------------------test code
            #
            #
            # with open('/home/eddie/dev/projects/python/visual_traceroute/test/test_route_data', 'rb') as f:
            #     route_list = pickle.load(f)
            #
            # self.draw_visual_trace_route(route_list)


            #-----------------------------------


            #
            #
            self.statusbar.clearMessage()
            self.statusbar.showMessage("Working...")
            self.doLookupPushButton.setEnabled(False)

            url = self.get_url()


            url = "www.microsoft.com";
            if url:
                # traceroute
                self.perform_traceroute(url)
            else:
                self.statusbar.showMessage("URL is empty", 5000)
                self.doLookupPushButton.setEnabled(True)


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
        # set up for visual traceroute
        hbx = QHBoxLayout()
        self.map.setLayout(hbx)
        web = QWebView()
        route_wrapper = RouteWrapper(route_list)
        web.page().mainFrame().addToJavaScriptWindowObject("route_list", route_wrapper)
        web.setHtml(html1)
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

        print("in RouteWrapper init....routes = " + str(self.routes))
        print("route size = " +str(len(self.routes)))

    @QtCore.pyqtSlot(result="int")
    def num_routes(self):
        return len(self.routes)

    @QtCore.pyqtSlot(int, result=str)
    def get_ip(self, offset):
        row = self.routes[offset]
        return str(row["query"])

    @QtCore.pyqtSlot(int, result=str)
    def get_longitude(self, offset):
        row = self.routes[offset]
        return str(row["lon"])

    @QtCore.pyqtSlot(int, result=str)
    def get_latitude(self, offset):
        row = self.routes[offset]
        return str(row["lat"])

    @QtCore.pyqtSlot(int, result=str)
    def get_ISP(self, offset):
        row = self.routes[offset]
        return str(row["isp"])

    @QtCore.pyqtSlot(int, result=str)
    def get_country(self, offset):
        row = self.routes[offset]
        return str(row["country"])

    @QtCore.pyqtSlot(int, result=str)
    def get_timezone(self, offset):
        row = self.routes[offset]
        return str(row["timezone"])

app = QApplication(sys.argv)
nu = VisualTraceRoute()
nu.show()
app.exec_()
