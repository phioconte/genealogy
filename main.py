""" Genealogy management program
 Author                        : Ph OCONTE
 Date                          : november 24, 2021
 Date of last update           : december 12, 2021
 Version                       : 1.0.0
"""
import sys
from PyQt5 import QtWidgets, uic, QtGui

from config import Config, ConfigMenu
from opendatabase import OpenDatabase, RenameDb
from display import DisplayIn, DisplayIndiv
from gedcomreadwrite import GedcomRead, GedcomWrite
from pdfwrite import PdfWrite
from htmlwrite import HtmlWrite
from eventmanagment import InputNewEvent, InputModifyEvent, InputDeleteEvent
from eventmanagment import EventSelectPhoto
from cities import ListCities, CitiesImportList
from tools import ToolsDbtoTxt, ToolsPrivatePublic, ToolsAnalysis
from about import AboutVersion, AboutTutorial, AboutLog
from individual import NewIndividual, UpdateIndividual
from util import CopyFile

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
        SaveDirectory = ""          # Saving Directory
        self.switch08.triggered.connect(self.MConfig)   # Configuration command

        """
        Tree management commands
        IndivList : Select individual
        Individual: Define the links of the individual
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
        self.Individual.itemClicked.connect(self.IndividualLink)
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
        switch14   : Rename the database
        switch01   : read csv families and cities files
        switch03   : write csv families and cities files
        switch02   : read GECOM file
        switch04   : write GEDCOM file
        switch05   : write website
        switch06   : write pdf file
        """
        self.switch00.triggered.connect(self.OpenDb)
        self.switch14.triggered.connect(self.RenameDb)
        self.switch01.triggered.connect(self.CsvR)
        self.switch03.triggered.connect(self.CsvW)
        self.switch02.triggered.connect(self.GedR)
        self.switch04.triggered.connect(self.GedW)
        self.switch05.triggered.connect(self.HtmlW)
        self.switch06.triggered.connect(self.PdfW)

        """
        management of a new event
        IndividualTable : Events table
        Button01        : New event
        """
        self.IndividualTable.itemClicked.connect(self.ShowMenuEvent)
        self.Button01.clicked.connect(self.NewEvent)
        self.CSelectPhoto.clicked.connect(self.PhotoEvent)

        """
        define indidual and links of individual
        switch09    : New individual
        switch10    : Define links of ,individual
        """
        self.switch09.triggered.connect(self.NewIndividual)
        self.switch10.triggered.connect(self.IndividualLink)

        """
        Tools
        switch11   : Database to *.txt file
        switch12   : Analyse database
        switch13   : Private to public
        switch15   : List of cities
        switch19   : Import cities list
        """
        self.switch11.triggered.connect(self.DbtoTxt)
        self.switch12.triggered.connect(self.Analyse)
        self.switch13.triggered.connect(self.Private)
        self.switch15.triggered.connect(self.Cities)
        self.switch19.triggered.connect(self.ImportCitiesList)

        """
        About
        switch16   : Version
        switch17   : Tutorial
        switch18   : Log
        """
        self.switch16.triggered.connect(self.Version)
        self.switch17.triggered.connect(self.Tutorial)
        self.switch18.triggered.connect(self.Log)

        """ Exit function: """
        self.switch07.triggered.connect(self.exit)

    def MConfig(self):          # Configuration command
        ConfigMenu(fen)
        return

    """=============================
    Tree management commands
    ShowMenu1      : Select individual
    IndividualLink : Define the links of the individual
    Spouse         : the spouse selected becomes the main individual
    BrSi           : the brother or sister selected becomes the main individual
    Child          : the child selected becomes the main individual
    Father         : the father becomes the main individual
    Mother         : the mother becomes the main individual
    Gpp            : The paternel grandfather becomes the main individual
    Gmp            : The paternel grandmother becomes the main individual
    Gmp            : The maternel grandfather becomes the main individual
    Gmm            : The maternel grandmother becomes the main individual
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

    def DeleteIndiv(self):
        return

    def IndividualLink(self):
        UpdateIndividual(fen)
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

    def RenameDb(self):
        RenameDb(fen)
        return

    def CsvR(self):
        return

    def CsvW(self):
        return

    def GedR(self):
        GedcomRead(fen)
        return

    def GedW(self):
        GedcomWrite(fen)
        return

    def HtmlW(self):
        HtmlWrite(fen)
        return

    def PdfW(self):
        PdfWrite(fen)
        return

    """
    management of a new event
    ShowMenuEvent  : Events table
    PhotoEvent     : Select the photo
    """

    def ShowMenuEvent(self, pos):
        menu2 = QtWidgets.QMenu(self)
        menu2.setTitle("ACTE")
        action21 = menu2.addAction(fen.mess["all15"], self.NewEvent)
        action22 = menu2.addAction(fen.mess["all16"], self.ModifyEvent)
        action23 = menu2.addAction(fen.mess["all14"], self.DeleteEvent)
        action2 = menu2.exec_(QtGui.QCursor.pos())
        return

    def NewEvent(self):
        InputNewEvent(fen)
        return

    def ModifyEvent(self):
        InputModifyEvent(fen)
        return

    def DeleteEvent(self):
        InputDeleteEvent(fen)
        return

    def PhotoEvent(self):
        EventSelectPhoto(fen)
        return

    """
    define indidual and links of individual
    NewIndividual    : New individual
    switch10         : Define links of ,individual
    """

    def NewIndividual(self):
        NewIndividual(fen)
        return

    """
    Tools
    DbtoTxt          : Database to *.txt file
    Analyse          : Analyse database
    Private          : Private to public
    ListCities       : List of cities
    ImportCitiesList : Import cities list
    """

    def DbtoTxt(self):
        ToolsDbtoTxt(fen)
        return

    def Analyse(self):
        ToolsAnalysis(fen)
        return

    def Private(self):
        ToolsPrivatePublic(fen)
        return

    def Cities(self):
        ListCities(fen)
        return

    def ImportCitiesList(self):
        CitiesImportList(fen)
        return

    """
    Tools
    Version    : Version
    Tutorial   : Tutorial
    Log        : Log
    """
    def Version(self):
        AboutVersion(self)
        return

    def Tutorial(self):
        AboutTutorial(self)
        return

    def Log(self):
        AboutLog(self)
        return

    """================================
    Exit software
    """

    def exit(self):
        """ Exit function """
        """ back up the database name_yyyymmddhhmmss.db """
        CopyFile(fen)
        self.close()
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
        self.statusbar.showMessage("%s\n" % (mes), 0)
        LogFile = "%s/log.txt" % (fen.SaveDirectory)
        """ Write to the log file """
        file = open(LogFile, 'a')
        file.write("%s\n" % (mes))
        file.close()
        return


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    fen = MyApp()

    fen.show()
    """ Read the configuration file """
    Config(fen)
    DisplayIn(fen)

    sys.exit(app.exec_())
