""" Individual managment
    Author                        : Ph OCONTE
    Date                          : december 6, 2021
    Last date of update           : december 8, 2021
    Version                       : 1.0.0
"""
import sqlite3

from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic

from dbmanagment import LinkDb, SelectTabDb, UpdateTabDb, InsertTabDb
from util import SelList, InitList
from display import DisplayIndiv
from eventmanagment import EventNewFamily

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
        SaveIndivUpdate(self, fen)
        return

    def IndivSave(self, fen):
        SaveIndivNew(self, fen)
        return

    def IndivSexe(self, fen):
        """ Define the list of possible spouses """
        if self.Sexe.currentIndex() == 0:
            return

        sexe = self.Sexe.currentText()

        conn = sqlite3.connect(LinkDb(fen))
        cursor = conn.cursor()
        if sexe == 'M':
            rows = SelectTabDb(fen, cursor, 'indiv', ('id', 'name', 'firstname'),
                               'sexe=?', ('F',), 1, 'ORDER BY name, firstname')
        else:
            rows = SelectTabDb(fen, cursor, 'indiv', ('id', 'name', 'firstname'),
                               'sexe=?', ('M',), 1, 'ORDER BY name, firstname')
        if rows:
            data = []
            for row in rows:
                line = "%s %s %s" % (row[0], row[1], row[2])
                data.append(line)
            SelList(data, self.Spouse, 1)
        cursor.close()
        conn.close()
        return

    def IndivName(self, fen):
        """ Adjust the list of possible fathers
        input:
            fen     : pointer to window
        output:
            nothing
        """
        name = name = "%s%%" % (self.Name.text().strip())
        conn = sqlite3.connect(LinkDb(fen))
        cursor = conn.cursor()

        params = ('id', 'name', 'firstname')
        rows = SelectTabDb(fen, cursor, 'indiv', params,
                           "name LIKE ? AND sexe='M'",
                           (name,),
                           1, 'ORDER BY name, firstname')
        if rows:
            dataFather = []
            dataMother = []
            for row in rows:
                line = ("%s %s %s" % (row[0], row[1], row[2]))
                dataFather.append(line)
                datas = self.IndivNameSpouse(fen, cursor, row[0])
                if datas is not None:
                    for data in datas:
                        dataMother.append(data)
            SelList(dataFather, self.Father, 1)
            dataMother.sort()
            SelList(dataMother, self.Mother, 1)
        cursor.close()
        conn.close()
        return

    def IndivNameSpouse(self, fen, cursor, id):
        """ Select the mothers
        input :
            fen     : pointer to window
            cursor  : pointer to database
            id      : father id
        """
        data = []
        rows = SelectTabDb(fen, cursor, 'fam', ('idw',), 'idh=?', (id,), 1, 'null')
        if rows:
            for row in rows:
                spouse = SelectTabDb(fen, cursor, 'indiv', ('id', 'name', 'firstname'),
                                     'id=?', (row[0],), 0, 'null')
                if spouse:
                    line = "%s %s %s" % (spouse[0], spouse[1], spouse[2])
                    data.append(line)
        return data


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
    """ Define a update individual
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
    indiv.Private.setCurrentText(fen.CPrivate.text())

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
    for i in range(60, 68):
        data = "label%02d" % (i)
        mesx = "lab%02d" % (i)
        getattr(indiv, data).setText(fen.mess[mesx])
    indiv.Exit.setText(fen.mess["lab68"])
    indiv.Update.setText(fen.mess["lab69"])
    indiv.Save.setText(fen.mess["lab70"])

    """ Sexe possible (M or F) """
    data = []
    data.append(fen.mess["all62"])
    data.append(fen.mess["all63"])
    SelList(data, indiv.Sexe, 1)

    """ Private/public """
    data = []
    data.append(fen.mess["all64"])
    data.append(fen.mess["all65"])
    SelList(data, indiv.Private, 0)

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


def SaveIndivUpdate(indiv, fen):
    """ Save the update data
    input:
        indiv   : pointer to update window
        fen     : pointer to window
    output:
        nothing
    """

    """ Update the definition of individual """
    data = [None, None, None, None, None, None, None]
    if len(indiv.Name.text()):
        data[0] = indiv.Name.text()
    if len(indiv.Firstname.text()):
        data[1] = indiv.Firstname.text()
    if indiv.Sexe.currentIndex() != 0:
        data[2] = indiv.Sexe.currentText()
    if indiv.Father.currentIndex() != 0:
        father = indiv.Father.currentText().split()
        if len(father) > 0:
            data[3] = father[0]
    if indiv.Mother.currentIndex() != 0:
        mother = indiv.Mother.currentText().split()
        if len(mother) > 0:
            data[4] = mother[0]
    data[5] = indiv.Private.currentIndex()
    data[6] = indiv.Id.text()

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()
    params = ('name', 'firstname', 'sexe', 'idfather', 'idmother', 'public')
    UpdateTabDb(fen, cursor, 'indiv', params, 'id=?', data)

    if indiv.Spouse.currentIndex() != 0:
        spouse = indiv.Spouse.currentText().split()
        if len(spouse) > 0:
            if data[2] == 'M':
                row = SelectTabDb(fen, cursor, 'fam', ('idh', 'idw'), 'idh=?  AND idw=?',
                                  (data[6], spouse[0]), 0, 'null')
            else:
                row = SelectTabDb(fen, cursor, 'fam', ('idh', 'idw'), 'idh=?  AND idw=?',
                                  (spouse[0], data[6]), 0, 'null')
            if not row:
                dataspouse = []
                if data[2] == 'M':
                    dataspouse.append(data[6])
                    dataspouse.append(spouse[0])
                else:
                    dataspouse.append(spouse[0])
                    dataspouse.append(data[6])
                EventNewFamily(fen, cursor, dataspouse)
    conn.commit()
    InitList(fen, cursor)
    cursor.close()
    conn.close()
    """ Afficher la mise à jour """
    data = "%s %s %s" % (data[6], data[0], data[1])
    DisplayIndiv(fen, data)

    indiv.close()
    return


def SaveIndivNew(indiv, fen):
    """ Save the new data
    input:
        indiv   : pointer to update window
        fen     : pointer to window
    output:
        nothing
    """

    """ Update the definition of individual """
    data = [None, None, None, None, None, None, None]

    data[0] = indiv.Id.text()
    if len(indiv.Name.text()):
        data[1] = indiv.Name.text()
    if len(indiv.Firstname.text()):
        data[2] = indiv.Firstname.text()
    if indiv.Sexe.currentIndex() != 0:
        data[3] = indiv.Sexe.currentText()
    if indiv.Father.currentIndex() != 0:
        father = indiv.Father.currentText().split()
        if len(father) > 0:
            data[4] = father[0]
    if indiv.Mother.currentIndex() != 0:
        mother = indiv.Mother.currentText().split()
        if len(mother) > 0:
            data[5] = mother[0]
    data[6] = indiv.Private.currentIndex()

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()
    params = ('id', 'name', 'firstname', 'sexe', 'idfather', 'idmother', 'public')
    InsertTabDb(fen, cursor, 'indiv', params, data)

    if indiv.Spouse.currentIndex() != 0:
        spouse = indiv.Spouse.currentText().split()
        if len(spouse) > 0:
            dataspouse = []
            if data[3] == 'M':
                dataspouse.append(data[0])
                dataspouse.append(spouse[0])
            else:
                dataspouse.append(spouse[0])
                dataspouse.append(data[0])
            EventNewFamily(fen, cursor, dataspouse)
    conn.commit()
    InitList(fen, cursor)
    cursor.close()
    conn.close()

    """ Afficher la mise à jour """
    data = "%s %s %s" % (data[0], data[1], data[2])
    DisplayIndiv(fen, data)

    indiv.close()
    return
