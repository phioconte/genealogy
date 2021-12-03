""" Cities list
    Author                        : Ph OCONTE
    Date                          : november 30, 2021
    Last date of update           : december 3, 2021
    Version                       : 1.0.0
"""
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic, QtGui

from dbmanagment import LinkDb, SelectTabDb, InsertTabDb, UpdateTabDb, DeleteTabDb

qtCreatorFile = "/home/philippe/Documents/QT_CREATION/genealogy_V1/cities.ui"

Ui_Dialog, QtBaseClass = uic.loadUiType(qtCreatorFile)


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
        self.PostalCode.setText(self.CityTable.item(self.CityTable.currentRow(), 2).text())
        self.InseeCode.setText(self.CityTable.item(self.CityTable.currentRow(), 3).text())
        self.Department.setText(self.CityTable.item(self.CityTable.currentRow(), 4).text())
        self.District.setText(self.CityTable.item(self.CityTable.currentRow(), 5).text())
        self.Country.setText(self.CityTable.item(self.CityTable.currentRow(), 6).text())
        """ Show Update and mask Save button """
        self.Update.setEnabled(True)
        self.Save.setEnabled(False)
        return

    def DeleteCity(self, fen):
        Id = self.CityTable.item(self.CityTable.currentRow(), 7).text()
        fen.Message("id : %s" % (Id))
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

def ListCities(fen):
    """ Show all the cities of the database
    input:
        WindowTitle : Window title
    output:
        nothing
    """

    """ Init the window cities """
    cities = CitiesManagment(fen)
    cities.setWindowTitle(fen.mess["all67"])
    cities.CityTable.clearContents()

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    rows = SelectTabDb(fen, cursor, 'city', ('*',), 'null', 0, 1,
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
    cities.exec()

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
    if cities.Locality.text() or cities.City.text() or cities.PostalCode.text() \
        or cities.InseeCode.text() or cities.Department.text()\
        or cities.District.text() or cities.Country.text():
        data = [None, None, None, None, None, None, None]
        if cities.Locality.text():
            data[0] = cities.Locality.text()
        if cities.City.text():
            data[1] = cities.City.text()
        if cities.PostalCode.text():
            data[2] = cities.PostalCode.text()
        if cities.InseeCode.text():
            data[3] = cities.InseeCode.text()
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
