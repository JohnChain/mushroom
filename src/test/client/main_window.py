#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from main_widget import *

class MyMainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):

        super(MyMainWindow, self).__init__(parent)
#         self.form_widget = FormWidget(self) 
#         self.setCentralWidget(self.form_widget)
        self.init() 
    def init(self):
        textEdit = QtGui.QTextEdit()
        self.setCentralWidget(textEdit)
        
        exitAction = QtGui.QAction(QtGui.QIcon('img/menus/exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        
        self.toolbar = self.addToolBar('exit1')
        self.toolbar.addAction(exitAction)
        self.toolbar = self.addToolBar('exit2')
        self.toolbar.addAction(exitAction)
        
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')
        
        self.setGeometry(300, 300, 500, 300)
#         self.setg
        self.setWindowTitle('Mushroom')
        
        self.form_widget = FormWidget(self)
        self.setCentralWidget(self.form_widget)
        self.show()
     
if __name__ == '__main__':
    app = QtGui.QApplication([])
    foo = MyMainWindow()
    foo.show()
    sys.exit(app.exec_())