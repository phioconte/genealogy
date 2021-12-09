""" Managment of events
    Author                        : Ph OCONTE
    Date                          : november 29, 2021
    Last date of update           : december 9, 2021
    Version                       : 1.0.0
"""
import os
import sqlite3
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, uic

from util import SelList, ReadFile
from dbmanagment import LinkDb, SelectTabDb, DeleteTabDb, InsertTabDb
from dbmanagment import UpdateTabDb
from display import DisplayIndiv
from reference import event_gb, event_fam
from cities import ListCitiesEvent
from warning import WarningMessage

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
        SaveEvent(self, fen)
        return

    def UpdateEvent(self, fen):
        UpdateEvent(self, fen)
        return

    def ExitEvent(self):
        self.close()
        return

    def NewCity(self, fen):
        ListCitiesEvent(self, fen)
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


def InputNewEvent(fen):
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


def InputModifyEvent(fen):
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


def InputDeleteEvent(fen):
    """ Delete an existing event
    input:
        fen     : pointer to window
    output:
        nothing
    """
    """ Read the id of the selected event """
    SelectIdEvent = fen.IndividualTable.item(fen.IndividualTable.currentRow(), 7).text()

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()
    DeleteTabDb(fen, cursor, 'event', 'id=?', (SelectIdEvent,))
    """ If event in event_fam, delete also family """
    conn.commit()
    cursor.close()
    conn.close()

    data = "%s %s %s" % (fen.CId.text(), fen.CName.text(), fen.CFirstname.text())
    """ Afficher la mise à jour """
    DisplayIndiv(fen, data)
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


def SaveEvent(event, fen):
    """ Save the new event
    input:
        event   : pointer to event window
        fen     : pointer to window
    output:
        nothing
    """

    """ Extract datas of event """
    data = EventData(event, fen)
    if data[0] is None:
        WarningMessage(event, fen.mess["all80"], fen.mess["all81"])
        return

    """ Insert data """
    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()
    params = ('idh', 'idw', 'type', 'day', 'month', 'year', 'city',
              'note', 'source', 'com1', 'precision', 'time')
    InsertTabDb(fen, cursor, 'event', params, data)
    if data[2] in event_fam:
        """ Define a new family """
        EventNewFamily(fen, cursor, data)
    conn.commit()
    cursor.close()
    conn.commit()

    data = "%s %s %s" % (fen.CId.text(), fen.CName.text(), fen.CFirstname.text())
    """ Show the new event """
    DisplayIndiv(fen, data)
    event.close()
    return


def UpdateEvent(event, fen):
    """ Update the datas of event
    input:
        event   : pointer to event window
        fen     : pointer to window
    output:
        nothing
    """
    """ Extract datas of event """
    data = []
    data = EventData(event, fen)
    if data[0] is None:
        WarningMessage(event, fen.mess["all80"], fen.mess["all81"])
        return

    id = fen.IndividualTable.item(fen.IndividualTable.currentRow(), 7).text()
    data.append(id)
    """ Update data """
    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()
    params = ('idh', 'idw', 'type', 'day', 'month', 'year', 'city',
              'note', 'source', 'com1', 'precision', 'time')
    UpdateTabDb(fen, cursor, 'event', params, 'id=?', data)
    if data[2] in event_fam:
        """ Define a new family """
        EventNewFamily(fen, cursor, data)
    conn.commit()
    cursor.close()
    conn.commit()

    data = "%s %s %s" % (fen.CId.text(), fen.CName.text(), fen.CFirstname.text())
    """ Show the update """
    DisplayIndiv(fen, data)
    event.close()
    return


def EventData(event, fen):
    """ Extract the datas of event
    input:
        event   : pointer to event window
        fen     : pointer to window
    output:
        data    : extract of datas
    """
    data = [None, None, None, None, None, None, None,
            None, None, None, None, None]
    """ Select the type of event """
    data[2] = event_gb[event.EEvent.currentIndex()]
    if data[2] in event_fam:
        if event.ESpouse.currentIndex() == 0\
            or len(event.ESpouse.currentText()) == 0:
            return data
    else:
        data[1] = event.EId.text()

    """ Select id """
    data[0] = event.EId.text()

    if event.EDay.text():
        data[3] = event.EDay.text()
    month = event.EMonth.currentIndex()
    if month != 0:
        data[4] = month
    if event.EYear.text():
        data[5] = event.EYear.text()
    city = event.ECity.currentIndex
    if city != 0:
        data[6] = EventExtractCity(fen, event.ECity.currentText())
    if event.ENote.text():
        data[7] = event.ENote.text()
    if event.ESource.text():
        data[8] = event.ESource.text()
    if event.EInformation.text():
        data[9] = event.EInformation.text()
    data[10] = event.EEstimate.currentIndex()
    if event.ETime.text():
        data[11] = event.ETime.text()
    """ Verify if spouse is define """
    if data[2] in event_fam:
        if event.ESpouse.currentIndex() != 0:
            spouse = event.ESpouse.currentText().split()
            if event.ESexe.currentText() == 'M':
                data[1] = spouse[0]
            else:
                data[1] = data[0]
                data[0] = spouse[0]
    return data


def EventExtractCity(fen, incity):
    """ Extract the complete city
    input:
        fen       : pointer to window
        incity    : city to define
    output
        outcity   : city
    """
    loccity = []
    outcity = None
    if len(incity) > 0:
        city = incity.split()
    else:
        return outcity

    loccity.append(city[0])
    loccity.append(' '.join(city[1:]))

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    params = ('locality', 'city', 'Insee', 'Postal', 'dep',
              'district', 'country')
    row = SelectTabDb(fen, cursor, 'city', params, 'Postal=? AND city=?',
                      (loccity), 0, 'null')
    if row:
        outcity = "%s,%s,%s,%s,%s,%s,%s" % (row[0], row[1], row[2], row[3],
                                            row[4], row[5], row[6])

    cursor.close()
    conn.close()
    return outcity

    return


def EventNewFamily(fen, cursor, data):
    """ If necessary, define a new family
    input:
        fen     : pointer to window
        cursor  : pointer to database
        event   : pointer to event window
        data    : data of event
    output:
        nothing
    """
    row = SelectTabDb(fen, cursor, 'fam', ('*',), 'idh=? AND idw=?',
                      (data[0], data[1]), 0, 'null')
    if row:
        return
    """ Create the new family """
    fam = SelectTabDb(fen, cursor, 'fam', ('id',), 'null', 0, 0,
                      'ORDER BY id DESC')
    if fam:
        i = int(fam[0]) + 1
    else:
        """ first family """
        i = 1
    fen.Message("Première famille : %s" % (i))
    InsertTabDb(fen, cursor, 'fam', ('id', 'idh', 'idw'),
                (i, data[0], data[1]))
    return


def EventSelectPhoto(fen):
    """
    Search the photo for the individual id selected
    input:
        fen     : pointer to window
    output:
        nothing
    """

    """ Ask the file to read """
    photo = ReadFile(fen, fen.mess["all40"], fen.mess["all41"],
                     "*.jpg", fen.mess["all42"], fen.WorkingDirectory)
    extension = os.path.splitext(photo)

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()
    if photo:
        params = ('indiv', 'file', 'form')
        values = (fen.CId.text(), photo, extension[1][1:])
        InsertTabDb(fen, cursor, 'object', params, values)

        """ Show the photo """
        image = photo
        pixmap = QPixmap(image)
        fen.CPhoto.setPixmap(pixmap)

    conn.commit()
    cursor.close()
    conn.close()
    return
