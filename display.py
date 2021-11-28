""" Display the data from database
 Author                        : Ph OCONTE
 Date                          : november 27, 2021
 Date of last update           : november 28, 2021
 Version                       : 1.0.0
"""
import sqlite3
import datetime
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QPixmap

from dbmanagment import LinkDb, DefDb, SelectTabDb, CountTabDb
from util import InitList, ReadEventSexe
from reference import dateap_gb, event_gb


def DisplayIn(fen):
    """
    Read the database
    input:
        fen     : pointeur sur la fenetre
    output:
        nothing
    """
    DbRead(fen)
    return


def DbRead(fen):
    """
    Read the database
    input:
        fen     : pointer to window
    output:
        nothing
    """

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    """ Generate tables if they do not exist """
    DefDb(fen, conn, cursor)

    """ Read all of the individual data """
    InitList(fen, cursor)

    """ Read all of the city data """
    # InitCity(fen, cursor)

    """ Count the number of families """
    nb = CountTabDb(fen, cursor, 'fam')
    fen.Message("%s %05d" % (fen.mess["all02"], nb[0]))
    """ Count the number of events """
    nb = CountTabDb(fen, cursor, 'event')
    fen.Message("%s %05d" % (fen.mess["all01"], nb[0]))
    """ Count the number of objects """
    nb = CountTabDb(fen, cursor, 'object')
    fen.Message("%s %05d" % (fen.mess["all04"], nb[0]))

    conn.commit()
    cursor.close()
    conn.close()

    return


def DisplayIndiv(fen, data):
    """
    Display of an individual as well as his ascendants and descendants
    input:
        fen     : pointer to window
        data    : id, name and first name of individual
    output:
        nothing
    """
    datas = data.split(' ')
    name = ' '.join(datas[1:])              # Name and firstname
    indiv = datas[0]                        # individual id
    fen.IndivSelect.setText(name)

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    """ Search the individual and is parents """
    fen.CId.setText(indiv)

    # fen.enapublic = 0
    fen.CName.clear()
    fen.CFirstname.clear()
    fen.CSexe.clear()
    # fen.CaPublic.setCurrentIndex(0)
    param = ('name', 'firstname', 'sexe', 'idfather', 'idmother', 'public')
    row = SelectTabDb(fen, cursor, 'indiv', param, 'id=?',
                      (indiv,), 0, 'null')
    if row:
        if row[0]:
            fen.CName.setText(row[0])
        if row[1]:
            fen.CFirstname.setText(row[1])
        if row[2]:
            fen.CSexe.setText(row[2])
    #    if int(row[5]) == 1:
    #        fen.CaPublic.setCurrentIndex(1)

    fen.Individual.clear()
    DisplayCasex(fen, indiv, fen.Individual, cursor, 1)
    if row[3]:
        DisplayParent(fen, row[3], fen.Father, fen.PaternelGrandFather,
                       fen.PaternelGrandMother, cursor)
    else:
        fen.Father.clear()
        fen.PaternelGrandFather.clear()
        fen.PaternelGrandMother.clear()
    if row[4]:
        DisplayParent(fen, row[4], fen.Mother, fen.MaternelGrandFather,
                      fen.MaternelGrandMother, cursor)
    else:
        fen.Mother.clear()
        fen.MaternelGrandFather.clear()
        fen.MaternelGrandMother.clear()

    """ Search spouse """
    DisplaySpouse(fen, indiv, row[2], cursor)

    """ Search children """
    DisplayChildren(fen, indiv, row[2], cursor)

    """ Search brothers and Sisters """
    DisplayBrSi(fen, indiv, row[3], row[4], cursor)

    """ Fill in the form """
    DisplayCasef(fen, indiv, cursor, row[2])

    conn.commit()
    cursor.close()
    conn.close()

    # fen.enapublic = 1
    return


def DisplayCasex(fen, indiv, case, cursor, flag):
    """
    Display data for an individual
    input:
        fen     : pointer to window
        indiv   : individual id
        case    : case to write
        cursor  : pointer to database
    output:
        nothing
    """

    if not indiv:
        return 0
    i = 0
    param = ('name', 'firstname', 'sexe', 'idfather', 'idmother', 'public')
    row = SelectTabDb(fen, cursor, 'indiv', param, 'id=?', (indiv,),
                      0, 'null')
    name = "%s" % (indiv)
    if row:
        if row[0]:
            name = "%s %s" % (name, row[0])
        if row[1]:
            name = "%s %s" % (name, row[1])
        case.insertItem(i, name)
        i += 1
    """ Display birth et death dates only for the main individual """
    if flag == 0:
        return

    """ Date of birth """
    event = ReadEventSexe(fen, indiv, row[2], 'BIRT', cursor)
    if event:
        date = DisplayDate(fen, event[0][0], event[0][1], event[0][2],
                           event[0][8])
        if row[2] == 'F':
            name = "%s : %s" % (fen.mess["all31"], date)
        else:
            name = "%s : %s" % (fen.mess["all30"], date)
        case.insertItem(i, name)
        i += 1

    """ Date of death """
    event = ReadEventSexe(fen, indiv, row[2], 'DEAT', cursor)
    if event:
        date = DisplayDate(fen, event[0][0], event[0][1], event[0][2],
                           event[0][8])
        if row[2] == 'F':
            name = "%s : %s" % (fen.mess["all33"], date)
        else:
            name = "%s : %s" % (fen.mess["all32"], date)
        case.insertItem(i, name)
        i += 1

    return


def DisplayDate(fen, day, month, year, precision):
    """
    convert date to gedcom format
    input:
        fen       : pointer to window
        day       : day of event
        month     : month of event
        year      : year of event
        precision : precision of event
    output:
        date      : date to gedcom format
    """
    date = ""

    if precision:
        date = dateap_gb[int(precision)]
    if day:
        date = "%s %s" % (date, day)
    if isinstance(month, (int)) and month != 0:
        mesx = "lis%02d" % (29 + int(month))
        date = "%s %s" % (date, fen.mess[mesx])
    if year:
        date = "%s %s" % (date, year)
    date = date.strip()

    return date


def DisplayParent(fen, indiv, Parent, GrandFather, GrandMother, cursor):
    """
    Display data of parents and grand parents
    input:
        fen         : pointer to window
        indiv       : individual id
        Parent      : case parent
        GrandFather : case grand father
        GranMother  : case grand mother
        cursor      : pointer to database
    output:
        nothing
    """
    Parent.clear()
    GrandFather.clear()
    GrandMother.clear()

    if indiv:
        DisplayCasex(fen, indiv, Parent, cursor, 1)
        """ Search maternel grand parents """
        param = ('name', 'firstname', 'sexe', 'idfather',
                 'idmother', 'public')
        gp = SelectTabDb(fen, cursor, 'indiv', param, 'id=?', (indiv,),
                         0, 'null')
        if gp:
            DisplayCasex(fen, gp[3], GrandFather, cursor, 1)
            DisplayCasex(fen, gp[4], GrandMother, cursor, 1)
        else:
            GrandFather.clear()
            GrandMother.clear()

    return


def DisplaySpouse(fen, indiv, sexe, cursor):
    """
    Display data for spouse
    input:
        fen     : pointer to window
        indiv   : id of individual
        sexe    : individual sexe
        cursor  : pointer to database
    output:
        nothing
    """

    fen.Spouse.clear()
    if sexe == 'F':
        spouses = SelectTabDb(fen, cursor, 'fam', ('idh',), 'idw=?',
                              (indiv,), 1, 'null')
    else:
        spouses = SelectTabDb(fen, cursor, 'fam', ('idw',), 'idh=?',
                              (indiv,), 1, 'null')
    if spouses:
        for spouse in spouses:
            if spouse[0]:
                DisplayCasex(fen, spouse[0], fen.Spouse, cursor, 0)

    return


def DisplayChildren(fen, indiv, sexe, cursor):
    """
    Display the data of children
    input:
        fen     : pointer to window
        indiv   : individual id
        sexe    : sexe of individual
        cursor  : pointer to database
    output:
        nothing
    """

    fen.Children.clear()
    if sexe == 'F':
        children = SelectTabDb(fen, cursor, 'indiv', ('id',),
                               'idmother=?', (indiv,), 1, 'null')
    else:
        children = SelectTabDb(fen, cursor, 'indiv', ('id',),
                               'idfather=?', (indiv,), 1, 'null')
    if children:
        for child in children:
            DisplayCasex(fen, child[0], fen.Children, cursor, 0)
    return


def DisplayBrSi(fen, indiv, idfather, idmother, cursor):
    """
    Display data to brothers and sisters
    input:
        fen     : pointer to window
        indiv   : individual id
        idfather: id of father
        idmother: id of mother
        cursor  : pointer to database
    output:
        nothing
    """
    fen.BrothersandSisters.clear()
    if idfather and idmother:
        BrSis = SelectTabDb(fen, cursor, 'indiv', ('id',),
                            'idfather=? AND idmother=? AND NOT id=?',
                            (idfather, idmother, indiv), 1, 'null')
        if BrSis:
            for BrSi in BrSis:
                DisplayCasex(fen, BrSi[0], fen.BrothersandSisters, cursor, 0)
    if idfather:
        if idmother is None:
            BrSis = SelectTabDb(fen, cursor, 'indiv', ('id',),
                                'idfather=? AND NOT id=?',
                                (idfather, indiv), 1, 'null')
        else:
            BrSis = SelectTabDb(fen, cursor, 'indiv', ('id',),
                                'idfather=? AND NOT idmother=? AND NOT id=?',
                                (idfather, idmother, indiv), 1, 'null')
        if BrSis:
            for BrSi in BrSis:
                DisplayCasex(fen, BrSi[0], fen.BrothersandSisters, cursor, 0)

    if idmother:
        if idfather is None:
            BrSis = SelectTabDb(fen, cursor, 'indiv', ('id',),
                                'idmother=? AND NOT id=?',
                                (idmother, indiv,), 1, 'null')
        else:
            BrSis = SelectTabDb(fen, cursor, 'indiv', ('id',),
                                'NOT idfather=? AND idmother=? AND NOT id=?',
                                (idfather, idmother, indiv,), 1, 'null')
        if BrSis:
            for BrSi in BrSis:
                DisplayCasex(fen, BrSi[0], fen.BrothersandSisters, cursor, 0)

    return


def DisplayCasef(fen, indiv, cursor, sexe):
    """
    Init the card
    input:
        fen     : pointer to window
        indiv   : individual id
        cursor  : pointer to database
        sexe    : sexe of individual
    output:
        nothing
    """

    bir_yea = 0                             # Year ob birth
    mar_age = 0                             # Age at time of marriage
    dea_age = 0                             # Age at time of death
    dee_age = 0                             # If not deceased, age to date

    fen.IndividualTable.clearContents()
    fen.CPhoto.clear()
    """ Show the photo of individual """
    fimages = SelectTabDb(fen, cursor, 'object', ('file', 'form'),
                          'indiv=?', (indiv,), 1, 'null')
    if fimages:
        for fimage in fimages:
            if fimage[0] and fimage[1]:
                if fimage[1] == 'jpg':
                    image = "%s" % (fimage[0])
                    pixmap = QPixmap(image)
                    fen.CPhoto.setPixmap(pixmap)

    """ Search for events related to the individual """
    Nbevent = 0
    i = 0
    for eve in event_gb:
        events = ReadEventSexe(fen, indiv, sexe, eve, cursor)
        if events:
            Nbevent += len(events)
            serifFont = QtGui.QFont("Times", 10)
            fen.IndividualTable.setRowCount(Nbevent)
            fen.IndividualTable.setFont(serifFont)
            for event in events:
                """ Type of event """
                event_lo = fen.LocEvent[event_gb.index(eve)-1]
                fen.IndividualTable.setItem(i, 0, QTableWidgetItem(event_lo))
                fen.IndividualTable.setItem(i, 7, QTableWidgetItem("%s" % (event[9])))
                """ Date of event """
                date = DisplayDate(fen, event[0], event[1], event[2],
                                   event[8])
                if eve == 'BIRT':
                    bir_yea = int(event[2])
                if eve == 'MARR':
                    """ Search the spouse """
                    spouse = DisplayCasefSpouse(fen, indiv, event[9], cursor)
                    if spouse:
                         fen.IndividualTable.setItem(i, 5, QTableWidgetItem(spouse))
                    if bir_yea > 1:
                        mar_age = int(event[2]) - bir_yea
                        fen.IndividualTable.setItem(i, 6, QTableWidgetItem("%s %s"
                                                    % (mar_age, fen.mess["all34"])))
                if eve == 'DEAT' and bir_yea > 1:
                    dea_age = int(event[2]) - bir_yea
                    fen.IndividualTable.setItem(i, 6, QTableWidgetItem("%s %s"
                                                % (dea_age, fen.mess["all34"])))
                fen.IndividualTable.setItem(i, 1, QTableWidgetItem(date))
                """ City of event """
                if event[3]:
                    city = event[3].split(',')
                    if city[3].isnumeric():
                        fen.IndividualTable.setItem(i, 2, QTableWidgetItem("%05d %s"
                                                    % (int(city[3]), city[1])))
                    else:
                        fen.IndividualTable.setItem(i, 2, QTableWidgetItem("%s %s"
                                                    % (city[3], city[1])))
                """ Note """
                if event[4]:
                    fen.IndividualTable.setItem(i, 3, QTableWidgetItem(event[4]))
                if event[5]:
                    fen.IndividualTable.setItem(i, 5, QTableWidgetItem(event[5]))
                if event[6]:
                    fen.IndividualTable.setItem(i, 4, QTableWidgetItem(event[6]))
                i += 1
    fen.IndividualTable.resizeColumnsToContents()
    fen.IndividualTable.resizeRowsToContents()

    fen.CAge.setStyleSheet("background: white")
    if bir_yea > 1 and dea_age == 0:
        date = datetime.datetime.now()
        age_dee = date.year - bir_yea
        fen.CAge.setText("%s %s" % (age_dee, fen.mess["all34"]))
        if age_dee > 99:
            fen.CAge.setStyleSheet("background: yellow")
    else:
        if dea_age > 0:
            fen.CAge.setText("%s %s" % (dea_age, fen.mess["all34"]))
        else:
            fen.CAge.setText("")

    return


def DisplayCasefSpouse(fen, indiv, id, cursor):
    """
    Init the data of spouse
    input:
        fen     : pointer to window
        indiv   : individual id
        id      : id of event
        cursor  : pointer to databases
    output:
        data    : name and firstname of spouse
    """
    data = ""
    ids = 0
    row = SelectTabDb(fen, cursor, 'event', ('idh', 'idw'), 'id=?',
                      (id,), 0, 'null')
    if row:
        if int(row[0]) == int(indiv):
            ids = row[1]
        else:
            ids = row[0]
        spouse = SelectTabDb(fen, cursor, 'indiv', ('name', 'firstname'),
                             'id=?', (ids,), 0, 'null')
        if spouse:
            data = "%s %s" % (spouse[0], spouse[1])
            return data

    return data
