""" Warning message
    Author                        : Ph OCONTE
    Date                          : december 9, 2021
    Last date of update           : december 9, 2021
    Version                       : 1.0.0
"""
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic, QtGui

qtCreatorFile = "/home/philippe/Documents/QT_CREATION/genealogy_V1/warning.ui"

Ui_Dialog, QtBaseClass = uic.loadUiType(qtCreatorFile)


class WarningManagment(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, fen):
        QtWidgets.QDialog.__init__(self, fen)
        Ui_Dialog.__init__(self)
        self.setupUi(self)


def WarningMessage(parent, mes1, mes2):
    """ Show a warning message
    input:
        fen     : pointer to window
        mes1    : Window title
        mes2    : Window message
    output:
        nothing
    """

    warning = WarningManagment(parent)
    warning.setWindowTitle(mes1)
    warning.Warning.setText(mes2)

    warning.exec()
    return
