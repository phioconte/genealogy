""" About
    Author                        : Ph OCONTE
    Date                          : december 4, 2021
    Last date of update           : december 6, 2021
    Version                       : 1.0.0
"""
import os
import datetime
import getpass
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic

from config import ConfigLogFile

data =['Date    : December 6, 2021',
       'Version : 1.0.0',
       'Author  : Philippe OCONTE',
       'Email   : <a href = "mailto:phi.oconte@gmail.com">phi.oconte@gmail.com</a>',
       'Ubuntu  : focal 20.04',
       'Python  : 3.8',
       'Qt      : 5']
qtCreatorFile = "/home/philippe/Documents/QT_CREATION/genealogy_V1/log.ui"
qtCreatorFileV = "/home/philippe/Documents/QT_CREATION/genealogy_V1/version.ui"

Ui_Dialog, QtBaseClass = uic.loadUiType(qtCreatorFile)
Ui_DialogV, QtBaseClass = uic.loadUiType(qtCreatorFileV)
ConfigFile = "config.txt"


class ShowLog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, fen):
        QtWidgets.QDialog.__init__(self, fen)
        Ui_Dialog.__init__(self)
        self.setupUi(self)


class ShowVersion(QtWidgets.QDialog, Ui_DialogV):
    def __init__(self, fen):
        QtWidgets.QDialog.__init__(self, fen)
        Ui_DialogV.__init__(self)
        self.setupUi(self)


def AboutVersion(fen):
    """ Show the window version """
    ver = ShowVersion(fen)
    ver.setWindowTitle(fen.mess["all69"])
    for line in data:
        ver.TextVersion.insertHtml("%s<br>" % (line))
    ver.exec()
    return


def AboutTutorial(fen):
    return


def AboutLog(fen):
    """ Show the log.txt file
    input:
        fen     : pointer to window
    output:
        nothing
    """
    file = ConfigLogFile(fen)
    read = open(file, 'r')
    lines = read.readlines()
    read.close()
    """ Show the window log """
    log = ShowLog(fen)
    log.setWindowTitle(fen.mess["all68"])
    for line in data:
        log.Log.insertHtml("%s<br>" % (line))
    for line in lines:
        log.Log.insertPlainText(line)
    log.exec()
    return
