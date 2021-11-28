""" Genealogy management program
 Author                        : Ph OCONTE
 Date                          : November 24, 2021
 Date of last update           : November 28, 2021
 Version                       : 1.0.0
"""
import sys
from PyQt5 import QtWidgets, uic, QtGui

from config import Config, ConfigMenu
from opendatabase import OpenDatabase
from display import DisplayIn, DisplayIndiv
from gedcomreadwrite import GedcomRead, GedcomWrite

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

        self.switch08.triggered.connect(self.MConfig)   # Configuration command

        """
        Tree management commands
        IndivList : Select individual
        Indiv     : Define the links of the individual
        Spouse    : the spouse selected becomes the main individual
        BrSi      : the brother or sister selected becomes the main individual
        Child     : the child selected becomes the main individual
        Father    : the father becomes the main individual
        Mother    : the mother becomes the main individual
        Gpp       : The paternel grandfather becomes the main individual
        Gmp       : The paternel grandmother becomes the main individual
        Gmp       : The maternel grandfather becomes the main individual
        Gmm       : The maternel grandmother becomes the main individual
        """
        self.IndivList.itemClicked.connect(self.ShowMenuIndivSelect)
        # self.Indiv.itemClicked.connect(self.UIndiv)
        self.Spouse.itemClicked.connect(self.SIndiv)
        self.BrothersandSisters.itemClicked.connect(self.BSIndiv)
        self.Children.itemClicked.connect(self.CIndiv)
        self.Father.itemClicked.connect(self.FIndiv)
        self.Mother.itemClicked.connect(self.MIndiv)
        self.PaternelGrandFather.itemClicked.connect(self.GppIndiv)
        self.PaternelGrandMother.itemClicked.connect(self.GmpIndiv)
        self.MaternelGrandFather.itemClicked.connect(self.GpmIndiv)
        self.MaternelGrandMother.itemClicked.connect(self.GmmIndiv)

        """
        Management of CSV, GEDCOM, HTML and PDF files
        switch00   : Open an existing database
        Rename     : Rename the database
        switch01   : read csv families and cities files
        CsvWrite   : write csv families and cities files
        switch02   : read GECOM file
        switch04   : write GEDCOM file
        HtmlWrite  : write website
        PdfWrite   : write pdf file
        """
        self.switch00.triggered.connect(self.OpenDb)
        # self.Rename.triggered.connect(self.RenameDb)
        # self.CsvRead.triggered.connect(self.CsvR)
        # self.CsvWrite.triggered.connect(self.CsvW)
        self.switch02.triggered.connect(self.GedR)
        self.switch04.triggered.connect(self.GedW)
        # self.HtmlWrite.triggered.connect(self.HtmlW)
        # self.PdfWrite.triggered.connect(self.PdfW)

    def MConfig(self):          # Configuration command
        ConfigMenu(fen)
        return

    """=============================
    Tree management commands
    ShowMenu1 : Select individual
    Spouse    : the spouse selected becomes the main individual
    BrSi      : the brother or sister selected becomes the main individual
    Child     : the child selected becomes the main individual
    Father    : the father becomes the main individual
    Mother    : the mother becomes the main individual
    Gpp       : The paternel grandfather becomes the main individual
    Gmp       : The paternel grandmother becomes the main individual
    Gmp       : The maternel grandfather becomes the main individual
    Gmm       : The maternel grandmother becomes the main individual
    """

    def ShowMenuIndivSelect(self, pos):
        menu1 = QtWidgets.QMenu(self)
        menu1.setTitle("INDIVIDUAL")
        action11 = menu1.addAction(fen.mess["all13"], self.SelectIndiv)
        action12 = menu1.addAction(fen.mess["all14"], self.DeleteIndiv)
        action1 = menu1.exec_(QtGui.QCursor.pos())

    def SelectIndiv(self):
        data = ' '.join(self.IndivList.currentItem().text().split())
        self.PrintIndiv(data)
        return

    def SIndiv(self):
        data = ' '.join(self.Spouse.currentItem().text().split())
        self.PrintIndiv(data)
        return

    def BSIndiv(self):
        data = ' '.join(self.BrothersandSisters.currentItem().text().split())
        self.PrintIndiv(data)
        return

    def CIndiv(self):
        data = ' '.join(self.Children.currentItem().text().split())
        self.PrintIndiv(data)
        return

    def FIndiv(self):
        data = ' '.join(self.Father.item(0).text().split())
        self.PrintIndiv(data)
        return

    def MIndiv(self):
        data = ' '.join(self.Mother.item(0).text().split())
        self.PrintIndiv(data)
        return

    def DeleteIndiv(self):
        return

    def GppIndiv(self):
        data = ' '.join(self.PaternelGrandFather.item(0).text().split())
        self.PrintIndiv(data)
        return

    def GmpIndiv(self):
        data = ' '.join(self.PaternelGrandMother.item(0).text().split())
        self.PrintIndiv(data)
        return

    def GpmIndiv(self):
        data = ' '.join(self.MaternelGrandFather.item(0).text().split())
        self.PrintIndiv(data)
        return

    def GmmIndiv(self):
        data = ' '.join(self.MaternelGrandMother.item(0).text().split())
        self.PrintIndiv(data)
        return

    def PrintIndiv(self, data):
        DisplayIndiv(fen, data)
        return

    """
    Management of CSV, GEDCOM, HTML and PDF files
    OpenDb     : Open an existing database
    RenameDb   : Rename the database
    CsvR       : read csv families and cities files
    CsvW       : write csv families and cities files
    GedR       : read GECOM file
    GedW       : write GEDCOM file
    HtmlW      : write website
    PdfW       : write pdf file
    """
    def OpenDb(self):
        OpenDatabase(fen)
        return

    def GedR(self):
        GedcomRead(fen)
        return

    def GedW(self):
        GedcomWrite(fen)
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
    DisplayIn(fen)

    sys.exit(app.exec_())

