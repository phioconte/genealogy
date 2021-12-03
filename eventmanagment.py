""" Managment of events
    Author                        : Ph OCONTE
    Date                          : november 29, 2021
    Last date of update           : december 3, 2021
    Version                       : 1.0.0
"""
import sqlite3
from PyQt5 import QtWidgets, uic

from util import SelList
from dbmanagment import LinkDb, SelectTabDb
from reference import event_gb, event_fam
from cities import ListCities

qtCreatorFile = "/home/philippe/Documents/QT_CREATION/genealogy_V1/event.ui"

Ui_Dialog, QtBaseClass = uic.loadUiType(qtCreatorFile)


class EventManagment(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, fen):
        QtWidgets.QDialog.__init__(self, fen)
        Ui_Dialog.__init__(self)
        self.setupUi(self)

        self.EEarth.clicked.connect(lambda: self.NewCity(fen))
        self.EEvent.currentTextChanged.connect(lambda: self.NewSpouse(fen))
        self.Save.clicked.connect(lambda: self.SaveEvent(fen))
        self.Update.clicked.connect(lambda: self.UpdateEvent(fen))
        self.Exit.clicked.connect(self.ExitEvent)

    def SaveEvent(self, fen):
        fen.Message("Save")
        self.close()
        return

    def UpdateEvent(self, fen):
        fen.Message("Update")
        self.close()
        return

    def ExitEvent(self):
        self.close()
        return

    def NewCity(self, fen):
        ListCities(fen)
        return

    def NewSpouse(self, fen):
        if self.EEvent.currentIndex() != 0:
            event = event_gb[1 + fen.LocEvent.index(self.EEvent.currentText())]
            if event in event_fam:
                self.label48.setHidden(False)
                self.ESpouse.setHidden(False)
                spouses = EventSelectSpouses(self, fen)
            else:
                self.label48.setHidden(True)
                self.ESpouse.setHidden(True)
        return

def NewEvent(fen):
    """ Define a new event
    input:
        fen     : pointer to window
    output:
        nothing
    """

    """ Show the window event """
    event = EventManagment(fen)
    event.setWindowTitle(fen.mess["all66"])

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    indiv = SelectTabDb(fen, cursor, 'indiv', ('*',), 'id=?',
                        (fen.CId.text(),), 0, 'null')

    if not indiv:
        return

    """ Init the inputs """
    EventInitList(fen, event, cursor)
    event.EId.setText(fen.CId.text())
    event.EName.setText(indiv[1])
    event.EFirstname.setText(indiv[2])
    event.ESexe.setCurrentText(indiv[3])
    event.EPrivate.setCurrentIndex(indiv[6])

    event.Update.setEnabled(False)
    event.Save.setEnabled(True)
    conn.commit()
    cursor.close()
    conn.close()
    event.exec()

    return


def ModifyEvent(fen):
    """ Modify an existing event
    input:
        fen     : pointer to window
    output:
        nothing
    """

    event = EventManagment(fen)
    event.setWindowTitle(fen.mess["all66"])

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    indiv = SelectTabDb(fen, cursor, 'indiv', ('*',), 'id=?',
                        (fen.CId.text(),), 0, 'null')

    if not indiv:
        return

    """ Init the inputs """
    event.Update.setEnabled(True)
    event.Save.setEnabled(False)
    EventInitList(fen, event, cursor)
    event.EId.setText(fen.CId.text())
    event.EName.setText(indiv[1])
    event.EFirstname.setText(indiv[2])
    event.ESexe.setCurrentText(indiv[3])
    event.EPrivate.setCurrentIndex(indiv[6])

    """ Read the id of the selected event """
    SelectIdEvent = fen.IndividualTable.item(fen.IndividualTable.currentRow(), 7).text()
    row = SelectTabDb(fen, cursor, 'event', ('*',), 'id=?', (SelectIdEvent,),
                      0, 'null')
    if row:
        event.EEvent.setCurrentIndex(event_gb.index(row[3]))
        if row[4] is not None:                  # day
            event.EDay.setText("%s" % (row[4]))
        if row[5] is not None:                  # month
            event.EMonth.setCurrentIndex(row[5])
        if row[6] is not None:                  # year
            event.EYear.setText("%s" % (row[6]))
        if row[7] is not None:                  # city
            city = row[7].split(',')
            line = "%s %s" % (city[3], city[1])
            event.ECity.setCurrentText(line)
        if row[8] is not None:                  # Note
            event.ENote.setText(row[8])
        if row[9] is not None:                  # Information
            event.EInformation.setText(row[9])
        if row[12] is not None:                 # Source
            event.ESource.setText(row[12])
        if row[14] is not None:                 # Time
            event.ETime.setText(row[14])
        if row[13] is not None:                 # Precision
            event.EEstimate.setCurrentIndex(int(row[13]))

        """ If event in event_fam, show spouse """
        if row[3] in event_fam:
            event.label48.setHidden(False)
            event.ESpouse.setHidden(False)
            """ recherche du conjoint """
            if row[2] == int(fen.CId.text()):
                idspouse = row[3]
                sexe = "M"
            else:
                idspouse = row[2]
                sexe = "F"
            data = []
            spouses = SelectTabDb(fen, cursor, 'indiv', ('id', 'name', 'firstname'),
                                  'sexe=?', (sexe,), 1, 'ORDER BY name, firstname')
            if spouses:
                for spouse in spouses:
                    line = "%s %s %s" % (spouse[0], spouse[1], spouse[2])
                    data.append(line)
                SelList(data, event.ESpouse, 1)
                spouserow = SelectTabDb(fen, cursor, 'indiv', ('id', 'name', 'firstname'),
                                        'id=?', (idspouse,), 0, 'null')
                if spouserow:
                    spousename = "%s %s %s" % (spouserow[0], spouserow[1],
                                               spouserow[2])
                    event.ESpouse.setCurrentText(spousename)
    conn.commit()
    cursor.close()
    conn.close()
    event.exec()
    return


def DeleteEvent(fen):
    """ Delete an existing event
    input:
        fen     : pointer to window
    output:
        nothing
    """
    return


def EventInitList(fen, event, cursor):
    """ Init the lists of the window
    input:
        fen     : pointer to first window
        event   : pointer to event window
        cursor  : pointer to database
    ouput
        nothing
    """

    """ Init the label """
    for i in range(40, 50):
        line = "label%02d" % (i)
        mesx = "lab%02d" % (i)
        getattr(event, line).setText(fen.mess[mesx])

    data = []
    """ Init the list of months """
    for i in range(30, 42):
        line = "lis%02d" % (i)
        data.append(fen.mess[line])
    SelList(data, event.EMonth, 1)

    """ Init the list of estimated date """
    data = []
    for i in range(50, 54):
        line = "lis%02d" % (i)
        data.append(fen.mess[line])
    SelList(data, event.EEstimate, 1)

    data = []
    """ Init the list of events """
    for i in range(0, 11):
        line = "lis%02d" % (i)
        data.append(fen.mess[line])
    SelList(data, event.EEvent, 1)

    """ Init sexe M / F """
    data = []
    data.append(fen.mess["all62"])
    data.append(fen.mess["all63"])
    SelList(data, event.ESexe, 0)

    """ Init private / public """
    data = []
    data.append(fen.mess["all64"])
    data.append(fen.mess["all65"])
    SelList(data, event.EPrivate, 0)

    """ Init city """
    data = []
    cities = SelectTabDb(fen, cursor, 'city', ('*',), 'null', 0, 1, 'ORDER BY city')
    if cities:
        for city in cities:
            line = "%s %s" % (city[4], city[2])
            data.append(line)
    if data:
        SelList(data, event.ECity, 1)

    """ Mask label48 and line spouse """
    event.label48.setHidden(True)
    event.ESpouse.setHidden(True)
    return

def EventSelectSpouses(event, fen):
    """ Select spouses
    input:
        fen     : pointer to first window
        event   : pointer to event window
        cursor  : pointer to database
    ouput
        data    : spouses
    """
    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    if event.ESexe.currentText() == 'M':
        spouses = SelectTabDb(fen, cursor, 'indiv', ('id', 'name', 'firstname'),
                              'sexe=?', ('F',), 1, 'ORDER BY name, firstname')
    else:
        spouses = SelectTabDb(fen, cursor, 'indiv', ('id', 'name', 'firstname'),
                              'sexe=?', ('M',), 1, 'ORDER BY name, firstname')
    if spouses:
        data = []
        for spouse in spouses:
            line = "%s %s %s" % (spouse[0], spouse[1], spouse[2])
            data.append(line)
        SelList(data, event.ESpouse, 1)

    cursor.close()
    conn.close()
    return
