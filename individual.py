""" Individual managment
    Author                        : Ph OCONTE
    Date                          : december 6, 2021
    Last date of update           : december 6, 2021
    Version                       : 1.0.0
"""
import sqlite3

from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic

from dbmanagment import LinkDb, SelectTabDb
from util import SelList

qtCreatorFile = "/home/philippe/Documents/QT_CREATION/genealogy_V1/individual.ui"

Ui_Dialog, QtBaseClass = uic.loadUiType(qtCreatorFile)


class ShowIndividual(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, fen):
        QtWidgets.QDialog.__init__(self, fen)
        Ui_Dialog.__init__(self)
        self.setupUi(self)

        self.Exit.clicked.connect(lambda: self.IndivExit(fen))
        self.Update.clicked.connect(lambda: self.IndivUpdate(fen))
        self.Save.clicked.connect(lambda: self.IndivSave(fen))
        self.Sexe.currentIndexChanged.connect(lambda: self.IndivSexe(fen))
        self.Name.textChanged.connect(lambda: self.IndivName(fen))

    def IndivExit(self, fen):
        self.close()
        return

    def IndivUpdate(self, fen):
        return

    def IndivSave(self, fen):
        return

    def IndivSexe(self, fen):
        return

    def IndivName(self, fen):
        return

def NewIndividual(fen):
    """ Define a new individual
    input:
        fen     : pointer to window
    output:
        nothing
    """

    indiv = ShowIndividual(fen)
    indiv.setWindowTitle(fen.mess["all70"])
    indiv.Update.setEnabled(False)
    indiv.Save.setEnabled(True)
    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()
    IndividualList(fen, indiv, cursor)

    """ Define the unique id of the individual """
    row = SelectTabDb(fen, cursor, 'indiv', ('id',), 'null', 0, 0,
                      'ORDER BY id DESC')
    if row:
        i = int(row[0]) + 1
    else:
        """ first individual """
        i = 1
    """ Set Id of individual in the tab """
    indiv.Id.setText("%s" % (i))
    cursor.close()
    conn.close()
    indiv.exec()

def UpdateIndividual(fen):
    """ Define a new individual
    input:
        fen     : pointer to window
    output:
        nothing
    """

    indiv = ShowIndividual(fen)
    indiv.setWindowTitle(fen.mess["all70"])
    indiv.Update.setEnabled(True)
    indiv.Save.setEnabled(False)

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    IndividualList(fen, indiv, cursor)

    """ Define the individual definition """
    indiv.Id.setText(fen.CId.text())
    indiv.Name.setText(fen.CName.text())
    indiv.Firstname.setText(fen.CFirstname.text())
    indiv.Sexe.setCurrentText(fen.CSexe.text())

    """ Define the spouse list """
    if fen.CSexe.text() == 'M':
        rows = SelectTabDb(fen, cursor, 'indiv', ('id', 'name', 'firstname'),
                           'sexe=?', ('F',), 1,
                           'ORDER BY name, firstname')
    else:
        rows = SelectTabDb(fen, cursor, 'indiv', ('id', 'name', 'firstname'),
                           'sexe=?', ('M',), 1,
                           'ORDER BY name, firstname')
    if rows:
        data = []
        for row in rows:
            line = "%s %s %s" % (row[0], row[1], row[2])
            data.append(line)
        SelList(data, indiv.Spouse, 1)

    if fen.Father.item(0) is not None:
        indiv.Father.setCurrentText(fen.Father.item(0).text())
    if fen.Mother.item(0) is not None:
        indiv.Mother.setCurrentText(fen.Mother.item(0).text())

    if fen.Spouse.item(0) is not None:
        indiv.Spouse.setCurrentText(fen.Spouse.item(0).text())
    cursor.close()
    conn.close()
    indiv.exec()

def IndividualList(fen, indiv, cursor):
    """ Initi the label
    input:
        fen     : pointer to window
        indiv   : pointer to indiv
        cursor  : pointer to database
    output:
        nothing
    """
    for i in range(60, 67):
        data = "label%02d" % (i)
        mesx = "lab%02d" % (i)
        getattr(indiv, data).setText(fen.mess[mesx])
    indiv.Exit.setText(fen.mess["lab67"])
    indiv.Update.setText(fen.mess["lab68"])
    indiv.Save.setText(fen.mess["lab69"])

    """ Sexe possible (M or F) """
    data = []
    data.append(fen.mess["all62"])
    data.append(fen.mess["all63"])
    SelList(data, indiv.Sexe, 1)

    """ Initi father list """
    data = []
    rows = SelectTabDb(fen, cursor, 'indiv', ('id', 'name', 'firstname'),
                       'sexe=?', ('M',), 1, 'ORDER BY name, firstname')
    if rows:
        for row in rows:
            line= "%s %s %s" % (row[0], row[1], row[2])
            data.append(line)
        SelList(data, indiv.Father, 1)

    """ Init mother list """
    data = []
    rows = SelectTabDb(fen, cursor, 'indiv', ('id', 'name', 'firstname'),
                       'sexe=?', ('F',), 1, 'ORDER BY name, firstname')
    if rows:
        for row in rows:
            line= "%s %s %s" % (row[0], row[1], row[2])
            data.append(line)
        SelList(data, indiv.Mother, 1)

    return
