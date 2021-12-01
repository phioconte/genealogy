""" Cities list
    Author                        : Ph OCONTE
    Date                          : november 30, 2021
    Last date of update           : december 1, 2021
    Version                       : 1.0.0
"""
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic, QtGui

from dbmanagment import LinkDb, SelectTabDb

qtCreatorFile = "/home/philippe/Documents/QT_CREATION/genealogy_V1/cities.ui"

Ui_Dialog, QtBaseClass = uic.loadUiType(qtCreatorFile)


class CitiesManagment(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, fen):
        QtWidgets.QDialog.__init__(self, fen)
        Ui_Dialog.__init__(self)
        self.setupUi(self)

        self.buttonBox.accepted.connect(lambda: self.Accepted(fen))
        self.buttonBox.rejected.connect(self.Rejected)

    def Accepted(self, fen):
        return

    def Rejected(self):
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
            i += 1
        cities.CityTable.resizeColumnsToContents()
        cities.CityTable.resizeRowsToContents()
    """ Init the label for new city """
    for i in range(10, 18):
        data = "label%02d" % (i)
        mesx = "col%02d" % (i)
        getattr(cities, data).setText(fen.mess[mesx])
    cities.exec()

    cursor.close()
    conn.close()
    return
