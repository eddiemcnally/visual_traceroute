import sys

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
# - only works with IP4, look at IP6
# - move stuff to config file (commands, google maps key, etc)
# - documentation
# - look at fixing hack for multiple markers on google maps



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
        self.routeListObjectWrapper = RouteWrapper()

        # set up buttons
        self.doLookupPushButton.setToolTip("start Trace Route")
        self.doLookupPushButton.clicked.connect(self.onClickDoItButton)
        self.doLookupPushButton.setAutoDefault(True)
        self.closePushButton.setToolTip("Exit application")
        self.closePushButton.clicked.connect(self.close)

        # set up menu handlers
        self.aboutMenuItem.triggered.connect(self.onAboutClicked)
        self.exitMenuItem.triggered.connect(self.close)

        # set up async worker thread
        self.traceRouteThreadedHandler = None

        # set up web view
        hbx = QHBoxLayout()
        self.map.setLayout(hbx)
        self.web = QWebView()
        self.web.page().mainFrame().javaScriptWindowObjectCleared.connect(self.addJavascriptObjects)
        self.web.page().mainFrame().addToJavaScriptWindowObject("route_list", self.routeListObjectWrapper)
        hbx.addWidget(self.web)
        self.web.show()


    @pyqtSlot()
    def addJavascriptObjects(self):
        """ Needed to repopulate the Javascript with the python objects each time the web page is refreshed
        :return: None
        """
        self.web.page().mainFrame().addToJavaScriptWindowObject("route_list", self.routeListObjectWrapper)


    @pyqtSlot()
    def onClickDoItButton(self):
        """ Called when the 'DoIt' button is pressed.
            Reads the entered URL, validates it and initiates the trace route command
        :return: None
        """
        try:
            self.statusbar.clearMessage()
            self.statusbar.showMessage("Working...")
            self.doLookupPushButton.setEnabled(False)
            self.textOutput.clear()

            # read entered URL
            url = self.urlLineEdit.text()

            if url:
                with open("./busy.html", "r") as htmlFile:
                    html = htmlFile.read()
                self.web.setHtml(html)

                self.traceRouteThreadedHandler = TraceRoute(url)

                # set up callbacks for the trace route output
                self.traceRouteThreadedHandler.traceRouteTerminated.connect(self.onTraceRouteComplete)
                self.traceRouteThreadedHandler.textOutputReady.connect(self.onTraceRouteRawOutput)

                self.traceRouteThreadedHandler.start()

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
    def onTraceRouteRawOutput(self, command_output):
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
    def onTraceRouteComplete(self, route_list):
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

            self.routeListObjectWrapper.clear()
            self.routeListObjectWrapper.add(route_list)
            self.web.page().mainFrame().addToJavaScriptWindowObject("route_list", self.routeListObjectWrapper)

            with open("./map_js.html", "r") as htmlFile:
                html = htmlFile.read()

            self.web.setHtml(html)

        except Exception as e:
            QMessageBox.critical(self,
                                 "Critical",
                                 "Problem performing TraceRoute command : " + str(e))

    @pyqtSlot()
    def onAboutClicked(self):
        box = QMessageBox.information(self, "About Visual TraceRoute", "Visual trace route")


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
