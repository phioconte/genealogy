""" About
    Author                        : Ph OCONTE
    Date                          : december 4, 2021
    Last date of update           : december 5, 2021
    Version                       : 1.0.0
"""
import os
import datetime
import getpass
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic

from config import ConfigLogFile

qtCreatorFile = "/home/philippe/Documents/QT_CREATION/genealogy_V1/log.ui"

Ui_Dialog, QtBaseClass = uic.loadUiType(qtCreatorFile)
ConfigFile = "config.txt"


class ShowLog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, fen):
        QtWidgets.QDialog.__init__(self, fen)
        Ui_Dialog.__init__(self)
        self.setupUi(self)


def AboutVersion(fen):
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
    for line in lines:
        log.Log.insertPlainText(line)
    log.exec()
    return
