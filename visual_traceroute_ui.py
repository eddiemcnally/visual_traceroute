# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'visual_traceroute_ui.ui'
#
# Created: Wed Apr 22 19:53:25 2015
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_visual_traceroute_main_window(object):
    def setupUi(self, visual_traceroute_main_window):
        visual_traceroute_main_window.setObjectName(_fromUtf8("visual_traceroute_main_window"))
        visual_traceroute_main_window.resize(780, 642)
        self.centralwidget = QtGui.QWidget(visual_traceroute_main_window)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.urlLineEdit = QtGui.QLineEdit(self.centralwidget)
        self.urlLineEdit.setGeometry(QtCore.QRect(20, 20, 331, 27))
        self.urlLineEdit.setObjectName(_fromUtf8("urlLineEdit"))
        self.doLookupPushButton = QtGui.QPushButton(self.centralwidget)
        self.doLookupPushButton.setGeometry(QtCore.QRect(370, 20, 98, 27))
        self.doLookupPushButton.setObjectName(_fromUtf8("doLookupPushButton"))
        self.closePushButton = QtGui.QPushButton(self.centralwidget)
        self.closePushButton.setGeometry(QtCore.QRect(660, 550, 98, 27))
        self.closePushButton.setObjectName(_fromUtf8("closePushButton"))
        self.visualTraceRouteWidget = QtGui.QWidget(self.centralwidget)
        self.visualTraceRouteWidget.setGeometry(QtCore.QRect(10, 70, 761, 461))
        self.visualTraceRouteWidget.setObjectName(_fromUtf8("visualTraceRouteWidget"))
        visual_traceroute_main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(visual_traceroute_main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 780, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        visual_traceroute_main_window.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(visual_traceroute_main_window)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        visual_traceroute_main_window.setStatusBar(self.statusbar)
        self.actionAbout = QtGui.QAction(visual_traceroute_main_window)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(visual_traceroute_main_window)
        QtCore.QMetaObject.connectSlotsByName(visual_traceroute_main_window)

    def retranslateUi(self, visual_traceroute_main_window):
        visual_traceroute_main_window.setWindowTitle(_translate("visual_traceroute_main_window", "Visual TraceRoute", None))
        self.urlLineEdit.setPlaceholderText(_translate("visual_traceroute_main_window", "Enter URL or IP Address", None))
        self.doLookupPushButton.setText(_translate("visual_traceroute_main_window", "Do it", None))
        self.closePushButton.setText(_translate("visual_traceroute_main_window", "Close", None))
        self.menuFile.setTitle(_translate("visual_traceroute_main_window", "File", None))
        self.menuHelp.setTitle(_translate("visual_traceroute_main_window", "Help", None))
        self.actionAbout.setText(_translate("visual_traceroute_main_window", "About", None))

