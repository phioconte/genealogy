""" Genealogy management program
 Author                        : Ph OCONTE
 Date                          : November 24, 2021
 Date of last update           : November 27, 2021
 Version                       : 1.0.0
"""
import sys
from PyQt5 import QtWidgets, uic

from config import Config, ConfigMenu
from opendatabase import OpenDatabase

qtCreatorFile = "/home/philippe/Documents/QT_CREATION/genealogy_V1/genealogy_V1.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        mess = ""                   # Pointer to the message dictionary
        LocEvent = ""               # Pointer to list od events
        WorkingDirectory = ""       # Working directory
        Database = ""               # Database file
        WebSite = ""                # Web site
        PdfFile = ""                # PDF file
        Language = "english"        # default initialization of the English language

        """ Configuration command """
        self.switch08.triggered.connect(self.MConfig)

        """ open an existing database """
        self.switch00.triggered.connect(self.OpenDb)

    def MConfig(self):          # Configuration command
        ConfigMenu(fen)
        return

    def OpenDb(self):           # Open an existing database
        OpenDatabase(fen)
        return

    def Message(self, mes):     # Show message to statusbar
        """
        Show message
        input:
            self    : pointer to window
            mes     : message to show
        output:
            nothing
        """
        # self.WriteTexte.insertPlainText("%s\n" % (mes))
        # self.log.insertPlainText("%s\n" % (mes))
        self.statusbar.showMessage("%s\n" % (mes), 0)
        return


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    fen = MyApp()

    fen.show()
    """ Read the configuration file """
    Config(fen)

    sys.exit(app.exec_())
