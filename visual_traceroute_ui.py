# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'visual_traceroute_ui.ui'
#
# Created: Mon May  4 21:40:33 2015
# by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_visual_traceroute_main_window(object):
    def setupUi(self, visual_traceroute_main_window):
        visual_traceroute_main_window.setObjectName("visual_traceroute_main_window")
        visual_traceroute_main_window.resize(780, 642)
        self.centralwidget = QtWidgets.QWidget(visual_traceroute_main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.urlLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.urlLineEdit.setGeometry(QtCore.QRect(20, 20, 331, 27))
        self.urlLineEdit.setObjectName("urlLineEdit")
        self.doLookupPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.doLookupPushButton.setGeometry(QtCore.QRect(370, 20, 98, 27))
        self.doLookupPushButton.setObjectName("doLookupPushButton")
        self.closePushButton = QtWidgets.QPushButton(self.centralwidget)
        self.closePushButton.setGeometry(QtCore.QRect(660, 550, 98, 27))
        self.closePushButton.setObjectName("closePushButton")
        self.visualTraceRouteWidget = QtWidgets.QWidget(self.centralwidget)
        self.visualTraceRouteWidget.setGeometry(QtCore.QRect(10, 70, 761, 461))
        self.visualTraceRouteWidget.setObjectName("visualTraceRouteWidget")
        self.tabWidget = QtWidgets.QTabWidget(self.visualTraceRouteWidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 761, 461))
        self.tabWidget.setObjectName("tabWidget")
        self.Text = QtWidgets.QWidget()
        self.Text.setObjectName("Text")
        self.textOutput = QtWidgets.QTextBrowser(self.Text)
        self.textOutput.setGeometry(QtCore.QRect(-5, 1, 761, 421))
        font = QtGui.QFont()
        font.setFamily("Courier 10 Pitch")
        self.textOutput.setFont(font)
        self.textOutput.setObjectName("textOutput")
        self.tabWidget.addTab(self.Text, "")
        self.map = QtWidgets.QWidget()
        self.map.setObjectName("map")
        self.tabWidget.addTab(self.map, "")
        visual_traceroute_main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(visual_traceroute_main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 780, 27))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        visual_traceroute_main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(visual_traceroute_main_window)
        self.statusbar.setObjectName("statusbar")
        visual_traceroute_main_window.setStatusBar(self.statusbar)
        self.aboutMenuItem = QtWidgets.QAction(visual_traceroute_main_window)
        self.aboutMenuItem.setObjectName("aboutMenuItem")
        self.exitMenuItem = QtWidgets.QAction(visual_traceroute_main_window)
        self.exitMenuItem.setObjectName("exitMenuItem")
        self.menuFile.addAction(self.exitMenuItem)
        self.menuHelp.addAction(self.aboutMenuItem)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(visual_traceroute_main_window)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(visual_traceroute_main_window)

    def retranslateUi(self, visual_traceroute_main_window):
        _translate = QtCore.QCoreApplication.translate
        visual_traceroute_main_window.setWindowTitle(_translate("visual_traceroute_main_window", "Visual TraceRoute"))
        self.urlLineEdit.setPlaceholderText(_translate("visual_traceroute_main_window", "Enter URL or IP Address"))
        self.doLookupPushButton.setText(_translate("visual_traceroute_main_window", "Do it"))
        self.closePushButton.setText(_translate("visual_traceroute_main_window", "Close"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Text),
                                  _translate("visual_traceroute_main_window", "Text"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.map), _translate("visual_traceroute_main_window", "Map"))
        self.menuFile.setTitle(_translate("visual_traceroute_main_window", "File"))
        self.menuHelp.setTitle(_translate("visual_traceroute_main_window", "Help"))
        self.aboutMenuItem.setText(_translate("visual_traceroute_main_window", "About"))
        self.exitMenuItem.setText(_translate("visual_traceroute_main_window", "Exit"))

