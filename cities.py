""" Cities list
    Author                        : Ph OCONTE
    Date                          : november 30, 2021
    Last date of update           : december 16, 2021
    Version                       : 1.0.0
"""

import os
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic, QtGui

from dbmanagment import LinkDb, SelectTabDb, InsertTabDb, UpdateTabDb, DeleteTabDb
from util import SelList, ReadFile
from warning import WarningMessage

""" Update december 16, 2021
    command read cities list file: update the cities for each event
"""

qtCreatorFile = "/home/philippe/Documents/QT_CREATION/genealogy_V1/cities.ui"
Ui_Dialog, QtBaseClass = uic.loadUiType(qtCreatorFile)

qtCreatorFile1 = "/home/philippe/Documents/QT_CREATION/genealogy_V1/citieslist.ui"
Ui_Dialog1, QtBaseClass = uic.loadUiType(qtCreatorFile1)


class CitiesManagment(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, fen):
        QtWidgets.QDialog.__init__(self, fen)
        Ui_Dialog.__init__(self)
        self.setupUi(self)

        self.CityTable.itemClicked.connect(lambda: self.ShowMenuCity(fen))
        self.Exit.clicked.connect(self.CityExit)
        self.Save.clicked.connect(lambda: self.SaveNewCity(fen))
        self.Update.clicked.connect(lambda: self.SaveNewCity(fen))

    def SaveNewCity(self, fen):
        SaveNewCity(self, fen)

    def ShowMenuCity(self, fen):
        menu1 = QtWidgets.QMenu(self)
        menu1.setTitle("CITY")
        action11 = menu1.addAction(fen.mess["all18"], lambda: self.ModifyCity(fen))
        action12 = menu1.addAction(fen.mess["all19"], lambda: self.DeleteCity(fen))
        action1 = menu1.exec_(QtGui.QCursor.pos())

    def ModifyCity(self, fen):
        self.Id.setText(self.CityTable.item(self.CityTable.currentRow(), 7).text())
        self.Locality.setText(self.CityTable.item(self.CityTable.currentRow(), 0).text())
        self.City.setText(self.CityTable.item(self.CityTable.currentRow(), 1).text())
        self.PCode.setText(self.CityTable.item(self.CityTable.currentRow(), 2).text())
        self.ICode.setText(self.CityTable.item(self.CityTable.currentRow(), 3).text())
        self.Department.setText(self.CityTable.item(self.CityTable.currentRow(), 4).text())
        self.District.setText(self.CityTable.item(self.CityTable.currentRow(), 5).text())
        self.Country.setText(self.CityTable.item(self.CityTable.currentRow(), 6).text())
        """ Show Update and mask Save button """
        self.Update.setEnabled(True)
        self.Save.setEnabled(False)
        return

    def DeleteCity(self, fen):
        Id = self.CityTable.item(self.CityTable.currentRow(), 7).text()
        conn = sqlite3.connect(LinkDb(fen))
        cursor = conn.cursor()
        DeleteTabDb(fen, cursor, 'city', 'id=?', (Id,))
        conn.commit()
        cursor.close()
        conn.close()
        self.close()
        return

    def CityExit(self):
        self.close()
        return

class CitiesInputList(QtWidgets.QDialog, Ui_Dialog1):
    def __init__(self, fen):
        QtWidgets.QDialog.__init__(self, fen)
        Ui_Dialog1.__init__(self)
        self.setupUi(self)

        self.TransfertIn.clicked.connect(lambda: self.InTransfert(fen))
        self.TransfertOut.clicked.connect(lambda: self.OutTransfert(fen))
        self.ChooseFile.clicked.connect(lambda: self.FileChoose(fen))
        self.buttonBox.clicked.connect(lambda: self.Accepted(fen))

    def InTransfert(self, fen):
        item = self.CityInput.currentRow()
        self.CitySelect.addItem(self.CityInput.item(item).text())
        self.CityInput.takeItem(item)
        return

    def OutTransfert(self, fen):
        item = self.CitySelect.currentRow()
        self.CityInput.addItem(self.CitySelect.item(item).text())
        self.CitySelect.takeItem(item)
        return

    def FileChoose(self, fen):
        file = ReadFile(fen, fen.mess["all82"], fen.mess["all83"],
                        '(*.txt *.csv)', fen.mess["all82"], fen.WorkingDirectory)
        self.FileSelect.setText(file)
        return

    def Accepted(self, fen):
        if len(self.FileSelect.text()) == 0:
            WarningMessage(self, fen.mess['all82'], fen.mess['all83'])
            return
        ExtractCities(self, fen)
        self.close()
        return


def ListCities(fen):
    """ Show all the cities of the database
    input:
        WindowTitle : Window title
    output:
        nothing
    """

    """ Init the window cities """
    cities = CitiesManagment(fen)
    cities = CitiesManagment(fen)

    ShowListCities(cities, fen)

    cities.exec()
    return


def ListCitiesEvent(event, fen):
    """ Init the window cities """
    cities = CitiesManagment(fen)

    ShowListCities(cities, fen)

    cities.exec()

    """ ReInit the CityList """
    event.ECity.clear()
    data = []
    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()
    citiesList = SelectTabDb(fen, cursor, 'city', ('*',), 'null', 0, 1, 'ORDER BY city')
    cursor.close()
    conn.close()
    if citiesList:
        for city in citiesList:
            line = ""
            if city[4] is not None:
                line = "%s" % (city[4])
            line = "%s %s" % (line, city[2])
            line = line.strip()
            data.append(line)
    if data:
        SelList(data, event.ECity, 1)
    if len(cities.PCode.text()) > 0:
        line = "%s" % (cities.PCode.text())
    line = "%s %s" % (line, cities.City.text())
    line = line.strip()
    # fen.Message(line)
    event.ECity.setCurrentText(line)
    return


def ShowListCities(cities, fen):
    """ Show all the cities of the database
    input:
        WindowTitle : Window title
    output:
        nothing
    """

    """ Init the window cities """
    cities.setWindowTitle(fen.mess["all67"])
    cities.CityTable.clearContents()

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    rows = SelectTabDb(fen, cursor, 'city',
                       ('id', 'locality', 'city', 'Postal', 'Insee', 'dep',
                        'district', 'country'), 'null', 0, 1,
                       'ORDER BY city')
    """ Init the header in the selected language """
    data = []
    for i in range(10, 17):
        col = "col%02d" % (i)
        data.append(fen.mess[col])
    cities.CityTable.setHorizontalHeaderLabels(data)
    cities.CityTable.setColumnHidden(7, True)
    if rows:
        i = 0
        Nbcities = len(rows)
        serifFont = QtGui.QFont("Times", 10)
        cities.CityTable.setRowCount(Nbcities)
        cities.CityTable.setFont(serifFont)
        for row in rows:
            for j in range(1, 8):
                if row[j] is not None:
                    cities.CityTable.setItem(i, j-1, QTableWidgetItem(row[j]))
                else:
                    cities.CityTable.setItem(i, j-1, QTableWidgetItem(""))
            line = "%s" % (row[0])
            cities.CityTable.setItem(i, 7, QTableWidgetItem(line))
            i += 1
        cities.CityTable.resizeColumnsToContents()
        cities.CityTable.resizeRowsToContents()
    """ Init the label for new city """
    for i in range(10, 18):
        data = "label%02d" % (i)
        mesx = "col%02d" % (i)
        getattr(cities, data).setText(fen.mess[mesx])
    """ Mask Update button """
    cities.Update.setEnabled(False)
    cities.Save.setEnabled(True)

    cursor.close()
    conn.close()
    return


def SaveNewCity(cities, fen):
    """ Save the new city
    input:
        cities  : pointer to city window
        fen     : pointer to the window
    output:
        nothing
    """
    if cities.Locality.text() or cities.City.text() or cities.PCode.text() \
        or cities.ICode.text() or cities.Department.text()\
        or cities.District.text() or cities.Country.text():
        data = [None, None, None, None, None, None, None]
        if cities.Locality.text():
            data[0] = cities.Locality.text()
        if cities.City.text():
            data[1] = cities.City.text()
        if cities.PCode.text():
            data[2] = "%05d" % (int(cities.PCode.text()))
        if cities.ICode.text():
            data[3] = "%05d" % (int(cities.ICode.text()))
        if cities.Department.text():
            data[4] = cities.Department.text()
        if cities.District.text():
            data[5] = cities.District.text()
        if cities.Country.text():
            data[6] = cities.Country.text()
        params = ('locality', 'city', 'postal', 'insee', 'dep',
                  'district', 'country')
        conn = sqlite3.connect(LinkDb(fen))
        cursor = conn.cursor()
        if cities.Id.text():        # update city
            data.append(cities.Id.text())
            UpdateTabDb(fen, cursor, 'city', params, 'id=?', data)
        else:
            InsertTabDb(fen, cursor, 'city', params, data)
        conn.commit()
        cursor.close()
        conn.close()
    cities.close()
    return


def CitiesImportList(fen):
    fen.Message("Import cities list")

    """ Init the window cities """
    cities = CitiesInputList(fen)

    """ Init the window cities """
    cities.setWindowTitle(fen.mess["all67"])

    """ Init the list of possible imputs """
    data = []
    for i in range(10, 17):
        mesx = "col%02d" % (i)
        data.append("%i %s" % (i-10, fen.mess[mesx]))
    SelList(data, cities.CityInput, 0)
    cities.exec()
    return


def ExtractCities(cities, fen):
    """ Extract cities from the file
    input:
        cities      : pointer to cities window
        fen         : pointer to window
    output:
        nothing
    """
    CityDef = ['locality', 'city', 'Postal', 'Insee', 'dep',
               'district', 'country']
    CityNb = 99
    PostalNb = 99
    InseeNb = 99
    """ read the file """
    read = open(cities.FileSelect.text(), "r")
    lines = read.readlines()

    params = []
    for i in range(0, cities.CitySelect.count()):
        item = cities.CitySelect.item(i).text().split()
        params.append(CityDef[int(item[0])])
        if CityDef[int(item[0])] == 'city':
            CityNb = i
        if CityDef[int(item[0])] == 'Postal':
            PostalNb = i
        if CityDef[int(item[0])] == 'Insee':
            InseeNb = i
    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()
    flag = 0
    for line in lines:
        line = line[:-1]
        if flag == 0:       # Mask the header line (first line)
            flag += 1
        else:
            data = []
            city = line.split(';')
            for i in range(0, len(params)):
                if len(city[i]) > 0:
                    if i == PostalNb:
                        data.append("%05d" % (int(city[i].strip())))
                    else:
                        if i == InseeNb:
                            data.append("%05d" % (int(city[i].strip())))
                        else:
                            data.append(city[i].strip())
                else:
                    data.append(None)
            """ check if the city already exists in the table """
            rows = None
            if data[CityNb] is not None and data[PostalNb] is not None:
                row = SelectTabDb(fen, cursor, 'city', ('*',),
                                  'city=? and Postal=?',
                                  (data[CityNb], data[PostalNb]), 0, 'null')
                if row:
                    data.append(data[CityNb])
                    data.append(data[PostalNb])
                    UpdateTabDb(fen, cursor, 'city', params, 'city=? and Postal=?',
                                data)
                else:
                    InsertTabDb(fen, cursor, 'city', params, data)
            else:
                if data[CityNb] is not None:
                    rows = SelectTabDb(fen, cursor, 'city', ('*',),
                                       'city=?', (data[CityNb],), 0, 'null')
                    if row:
                        data.append(data[CityNb])
                        UpdateTabDb(fen, cursor, 'city', params, 'city=?', data)
                    else:
                        InsertTabDb(fen, cursor, 'city', params, data)

    """ Update the cities in each event """
    rows = SelectTabDb(fen, cursor, 'event', ('id', 'city'), 'null', 0, 1, 'null')
    if rows:
        for row in rows:
            if row[1] is not None:
                city = row[1].split(',')
                data = []
                data.append(ExtractCitiesEvent(fen, cursor, city[1], city[3]))
                if data is not None:
                    data.append(row[0])
                    UpdateTabDb(fen, cursor, 'event', ('city',), 'id=?', data)
    conn.commit()
    cursor.close()
    conn.close()
    return


def ExtractCitiesEvent(fen, cursor, city, postal):
    cities = SelectTabDb(fen, cursor, 'city', ('*',), 'city=? AND Postal=?',
                         (city, postal), 0, 'null')
    line = None
    if cities:
        for i in range(1, len(cities)):
            if cities[i] is not None:
                if i == 1:
                    line = "%s" % (cities[i])
                else:
                    line = "%s,%s" % (line, cities[i])
    return line
