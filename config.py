""" Software configuration
    Author                        : Ph OCONTE
    Date                          : november 24, 2021
    Last date of update           : november 28, 2021
    Version                       : 1.0.0
"""
import copy
import os
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic

from messages import language, mess_gb, mestype
from dbmanagment import LinkDb, DefDb

qtCreatorFile = "/home/philippe/Documents/QT_CREATION/genealogy_V1/config.ui"

Ui_Dialog, QtBaseClass = uic.loadUiType(qtCreatorFile)
ConfigFile = "config.txt"


class Configuration(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, fen):
        QtWidgets.QDialog.__init__(self, fen)
        Ui_Dialog.__init__(self)
        self.setupUi(self)

        self.SelectWorkingDirectory.clicked.connect(self.CSelDir)
        self.SelectWebSite.clicked.connect(self.CSelWeb)
        self.buttonBox.accepted.connect(self.Accepted)
        self.buttonBox.rejected.connect(self.Rejected)

    def CSelDir(self):                  # Select working directory
        SelectWorkingDirectory(self)
        return

    def CSelWeb(self):                  # Select web site
        SelectWebSite(self)

    def Accepted(self):                 # Write the config.txt file
        WriteConfigFile(self)

    def Rejected(self):
        return


def ConfigMenu(fen):
    """
    Execute the configuration command
    input :
        fen     : pointer to window
    output:
        nothing
    """
    conf = Configuration(fen)

    """ If config.txt file exists init it """
    if os.path.exists(ConfigFile):
        read = open(ConfigFile, "r")
        lines = read.readlines()
        read.close()
        for i in range(0, len(lines)):
            if i == 0:          # working directory
                conf.WorkingDirectory.setText(lines[i][0:-1])
            if i == 1:          # database
                conf.Database.setText(lines[i][0:-1])
            if i == 2:          # HTML Web site
                conf.WebSiteDirectory.setText(lines[i][0:-1])
            if i == 3:          # PDF file
                conf.PdfFile.setText(lines[i][0:-1])
            if i == 4:
                conf.Language.setCurrentText(lines[i][0:-1])

    conf.exec()

    if len(conf.WorkingDirectory.text()) == 0 \
        or len(conf.Database.text()) == 0 \
        or len(conf.WebSiteDirectory.text()) == 0 \
        or len(conf.PdfFile.text()) == 0:
        return 0
    else:
        fen.WorkingDirectory = copy.deepcopy(conf.WorkingDirectory.text())
        fen.Database = copy.deepcopy(conf.Database.text())
        fen.WebSite = copy.deepcopy(conf.WebSiteDirectory.text())
        fen.PdfFile = copy.deepcopy(conf.PdfFile.text())
        fen.Language = copy.deepcopy(conf.Language.currentText())
        fen.mess = copy.deepcopy(mestype[language.index(
                             conf.Language.currentText())])
    ReadConfig(fen)
    return 1


def SelectWorkingDirectory(conf):
    """
    Select the working directory
    input :
        conf : pointer to window
    output:
        nothing
    """
    conf.WorkingDirectory.setText(QFileDialog.getExistingDirectory(conf,
                                  "Select Directory"))
    return


def SelectWebSite(conf):
    """
    Select the web site directory
    input :
        conf : pointer to window
    output:
        nothing
    """
    WebSiteDirectory = QFileDialog.getExistingDirectory(conf,
                                                        "Select Directory")
    conf.WebSiteDirectory.setText("%s/website" % (WebSiteDirectory))
    return


def WriteConfigFile(conf):
    """
    Saving the config.txt file
    input :
        conf : pointer to window
    output:
        nothing
    """


    if len(conf.WorkingDirectory.text()) == 0 \
           or len(conf.Database.text()) == 0 \
           or len(conf.WebSiteDirectory.text()) == 0 \
           or len(conf.PdfFile.text()) == 0:
        return 0

    Database = conf.Database.text().split('.')
    if Database[-1] == "db":
        RefDatabase = conf.Database.text()
    else:
        RefDatabase = "%s.db" % (conf.Database.text())

    PdfFile = conf.PdfFile.text().split('.')
    if PdfFile[-1] == "pdf":
        RefPdfFile = conf.PdfFile.text()
    else:
        RefPdfFile = "%s.pdf" % (conf.PdfFile.text())

    write = open(ConfigFile, "w")
    if write:
        write.write("%s\n" % (conf.WorkingDirectory.text()))
        write.write("%s\n" % (RefDatabase))
        write.write("%s\n" % (conf.WebSiteDirectory.text()))
        write.write("%s\n" % (RefPdfFile))
        write.write("%s\n" % (conf.Language.currentText()))
        write.close()
    return 1


def Config(fen):
    """
    Initialize the list of accepted languages
    input :
        fen     : pointer to window
    output:
        nothing
    """

    """  if config.txt file exists, init the labels """
    if os.path.exists(ConfigFile):
        ReadConfig(fen)                 # Read the config file
        return
    else:
        i = 0
        while i == 0:
            i = ConfigMenu(fen)         # Config the program
        ReadConfig(fen)
    return


def ReadConfig(fen):
    """ read the config.txt file
    input :
        fen     : pointer to window
    output:
        Nothing
    """

    """ By default initialize the english version of messages """
    fen.mess = copy.deepcopy(mess_gb)

    """ Read the config.txt file """
    read = open(ConfigFile, "r")
    lines = read.readlines()
    read.close()
    for i in range(0, len(lines)):
        if i == 0:          # working directory
            fen.WorkingDirectory = copy.deepcopy(lines[i][0:-1])
        if i == 1:          # database
            fen.Database = copy.deepcopy(lines[i][0:-1])
        if i == 2:          # HTML Web site
            fen.WebSite = copy.deepcopy(lines[i][0:-1])
        if i == 3:          # PDF file
            fen.PdfFile = copy.deepcopy(lines[i][0:-1])
        if i == 4:
            fen.Language = copy.deepcopy(lines[i][0:-1])
            fen.mess = copy.deepcopy(mestype[language.index(
                                      lines[i][0:-1])])

    ConfigInitMenu(fen)     # Initialize the menu labels
    ConfigInitLabel(fen)    # Initialize the labels
    ConfigInitList(fen)     # Initialize the lists
    """ create the database if doesn't exist """
    ConfigCreateDb(fen)
    return

def ConfigInitMenu(fen):
    """
    Initialization of the menu labels in the chosen language
    input :
        fen : pointer to window
    output:
        nothing
    """
    for i in range(0, 6):
        data = "menu%02d" % (i)
        mesx = "men%02d" % (i)
        getattr(fen, data).setTitle(fen.mess[mesx])

    for i in range(0, 14):
        data = "switch%02d" % (i)
        mesx = "swi%02d" % (i)
        getattr(fen, data).setText(fen.mess[mesx])
    return


def ConfigInitLabel(fen):
    """
    Initialization the labels in the chosen language
    input :
        fen : pointer to window
    output:
        nothing
    """
    for i in range(0, 5):
        data = "label%02d" % (i)
        mesx = "lab%02d" % (i)
        getattr(fen, data).setText(fen.mess[mesx])
    return


def ConfigInitList(fen):
    """
    Initialization the lists in the chosen language
    input :
        fen : pointer to window
    output:
        nothing
    """
    data = []
    for i in range(0, 11):
        lis = "lis%02d" % (i)
        data.append(fen.mess[lis])
    fen.LocEvent = copy.deepcopy(data)

    data = []
    for i in range(0, 8):
        col = "col%02d" % (i)
        data.append(fen.mess[col])

    fen.IndividualTable.setHorizontalHeaderLabels(data)
    fen.IndividualTable.setColumnHidden(7, True)

def ConfigSaveUpdate(fen, file):
    """ Update the config.txt file
    input:
        fen     : pointer to window
        file    : database file
    ouput:
        noting
    """

    FileName = os.path.basename(file)
    FileDirectory = os.path.dirname(file)

    """ Read the config.txt file """
    read = open(ConfigFile, "r")
    lines = read.readlines()
    read.close()

    """ Write the config.txt update file """
    write = open(ConfigFile, "w")
    write.write("%s\n" % (FileDirectory))
    write.write("%s\n" % (FileName))

    i = 0
    for line in lines:
        if i > 1:
            write.write(line)
        i += 1
    write.close()
    return


def ConfigCreateDb(fen):
    """ Read the database
    input:
        fen     : pointer to window
    ouput:
        noting
    """
    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()
    DefDb(fen, conn, cursor)
    conn.commit()
    cursor.close()
    conn.close()
    return
