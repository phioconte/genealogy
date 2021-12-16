""" Definition of tools
 Author                        : Ph OCONTE
 Date                          : november 30, 2021
 Date of last update           : december 14, 2021
 Version                       : 1.1.0
"""
import sqlite3
import datetime

from dbmanagment import LinkDb, SelectTabDb, UpdateTabDb
from util import WriteFile


def ToolsDbtoTxt(fen):
    """
    write to file txt tables of database
    input:
        fen     : pointer to window
    output:
        nothing
    """

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    """ Save file """
    sav = WriteFile(fen, fen.mess["all36"], fen.mess["all35"], "*.txt",
                    fen.mess["all07"], fen.WorkingDirectory)
    if not sav:
        return
    """ Open the file to write """
    sav_wri = open(sav, "w")
    if not sav_wri:
        return

    """ Write the individuals table """
    ToolsDbtoTxtIndividualList(fen, cursor, sav_wri)

    """ Write the events list """
    ToolsDbtoTxtEventList(fen, cursor, sav_wri)

    """ Save families """
    ToolsDbtoTxtFamList(fen, cursor, sav_wri)

    """ Save objects """
    sav_wri.write("Objects list\n")
    rows = SelectTabDb(fen, cursor, 'object', ('*',), 'null', 0, 1,
                       'ORDER BY id')
    if rows:
        for row in rows:
            sav_wri.write("Id object : %4s\n" % (row[1]))
            sav_wri.write("\tId individual : %s\n" % (row[2]))
            sav_wri.write("\tfile          : %s\n" % (row[3]))

    """ Save cities """
    ToolsDbtoTxtCityList(fen, cursor, sav_wri)

    sav_wri.close()
    cursor.close()
    conn.close()
    fen.Message(fen.mess["all44"])
    return


def ToolsDbtoTxtIndividualList(fen, cursor, wri):
    """ Write the list of individuals
    input:
        fen     : pointer to window
        cursor  : pointer to database
        wri     : file to write
    output:
        nothing
    """
    wri.write("Individuals list\n")
    rows = SelectTabDb(fen, cursor, 'indiv', ('*',), 'null', 0,  1,
                       'ORDER BY name, firstname')
    if rows:
        for row in rows:
            wri.write("%4s: %s %s\n" % (row[0], row[1], row[2]))
            wri.write("\tSexe           : %s\n" % (row[3]))
            wri.write("\tId father      : %s\n" % (row[4]))
            wri.write("\tId mother      : %s\n" % (row[5]))
            wri.write("\tPublic/private : %s\n" % (row[6]))
    return


def ToolsDbtoTxtEventList(fen, cursor, wri):
    """ Write the list of events
    input:
        fen     : pointer to window
        cursor  : pointer to database
        wri     : file to write
    output:
        nothing
    """
    wri.write("Events list\n")
    rows = SelectTabDb(fen, cursor, 'event', ('*',), 'null', 0, 1,
                       'ORDER BY type')
    if rows:
        for row in rows:
            wri.write("%4s: %4s %4s => %s\n" % (row[0], row[1], row[2],
                      row[3]))
            wri.write("\tDate      : %s/%s/%s\n" % (row[5], row[4], row[6]))
            wri.write("\tCity      : %s\n" % (row[7]))
            wri.write("\tNote      : %s\n" % (row[8]))
            wri.write("\tCom1      : %s\n" % (row[9]))
            wri.write("\tSource    : %s\n" % (row[12]))
            wri.write("\tPrécision : %s\n" % (row[13]))
            wri.write("\tTime      : %s\n" % (row[14]))
    return


def ToolsDbtoTxtFamList(fen, cursor, wri):
    """ Write the list of families
    input:
        fen     : pointer to window
        cursor  : pointer to database
        wri     : file to write
    output:
        nothing
    """
    wri.write("Families list\n")
    rows = SelectTabDb(fen, cursor, 'fam', ('*',), 'null', 0, 1,
                       'ORDER BY id')
    if rows:
        for row in rows:
            wri.write("Id famille : %4s\n" % (row[0]))
            wri.write("\tId Father : %s\n" % (row[1]))
            wri.write("\tId Mother : %s\n" % (row[2]))
    return


def ToolsDbtoTxtObjectList(fen, cursor, wri):
    """ Write the list of objects
    input:
        fen     : pointer to window
        cursor  : pointer to database
        wri     : file to write
    output:
        nothing
    """
    wri.write("Objects list\n")
    rows = SelectTabDb(fen, cursor, 'object', ('*',), 'null', 0, 1,
                       'ORDER BY id')
    if rows:
        for row in rows:
            wri.write("Id object : %4s\n" % (row[0]))
            wri.write("\tId individual : %s\n" % (row[2]))
            wri.write("\tfile          : %s\n" % (row[3]))
    return


def ToolsDbtoTxtCityList(fen, cursor, wri):
    """ Write the list of cities
    input:
        fen     : pointer to window
        cursor  : pointer to database
        wri     : file to write
    output:
        nothing
    """
    wri.write("Cities list\n")
    rows = SelectTabDb(fen, cursor, 'city', ('id', 'locality', 'city',
                       'Postal', 'Insee', 'dep', 'district',
                       'country'), 'null', 0, 1, 'ORDER BY city')
    if rows:
        for row in rows:
            wri.write("Id city : %4s\n" % (row[0]))
            wri.write("\tLocality    : %s\n" % (row[1]))
            wri.write("\tCity        : %s\n" % (row[2]))
            if row[3] is not None:
                if row[3].isnumeric():
                    wri.write("\tPOSTAL code : %05d\n" % (int(row[3])))
            if row[4] is not None:
                if row[4].isnumeric():
                    wri.write("\tINSEE code  : %05d\n" % (int(row[4])))
            wri.write("\tDepartment  : %s\n" % (row[5]))
            wri.write("\tDistrict    : %s\n" % (row[6]))
            wri.write("\tCountry     : %s\n" % (row[7]))
    return


def ToolsPrivatePublic(fen):
    """
    For each individual if the birth is 100 years old or if he is death
        the datas are public
    else the data are private
    input:
        fen     : pointer to window
    output:
        nothing
    """
    """ define the actuel date """
    date = datetime.datetime.now()
    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    """ All datas of individuals are private """
    rows = SelectTabDb(fen, cursor, 'indiv', ('*',),
                       'null', 0, 1, 'null')
    if rows:
        for row in rows:
            UpdateTabDb(fen, cursor, 'indiv', ('public',),
                        'id=?', (0, row[0]))

    conn.commit()

    """ if birth of individual > 99 => datas are public """
    ToolsPrivatePublicBirt(fen, cursor, date)
    conn.commit()

    """ if individual is death => datas are public """
    ToolsPrivatePublicDeath(fen, cursor, date)
    conn.commit()

    """ if wedding 80 years old => datas are public """
    ToolsPrivatePublicWedding(fen, cursor, date)
    conn.commit()

    cursor.close()
    conn.close()
    fen.Message(fen.mess["all44"])
    return


def ToolsPrivatePublicBirt(fen, cursor, date):
    """ If birth > 99 ans datas of individuals are public
    input:
        fen     : pointer to window
        cursor  : pointer to database
    output:
        nothing
    """
    rows = SelectTabDb(fen, cursor, 'indiv', ('*',),
                       'null', 0, 1, 'null')
    if rows:
        for row in rows:
            event = SelectTabDb(fen, cursor, 'event', ('year',),
                                '(idh=? OR idw=?) AND type=?',
                                (row[0], row[0], 'BIRT'), 0, 'null')
            if event:
                if event[0]:
                    if date.year - int(event[0]) > 99:
                        UpdateTabDb(fen, cursor, 'indiv', ('public',),
                                    'id=?', (1, row[0]))
    return


def ToolsPrivatePublicDeath(fen, cursor, date):
    """ if individual is death => datas are public
    input:
        fen     : pointer to window
        cursor  : pointer to database
    output:
        nothing
    """
    rows = SelectTabDb(fen, cursor, 'indiv', ('*',),
                       'null', 0, 1, 'null')
    if rows:
        for row in rows:
            event = SelectTabDb(fen, cursor, 'event', ('*',),
                                '(idh=? OR idw=?) AND type=?',
                                (row[0], row[0], 'DEAT'), 0, 'null')
            if event:
                UpdateTabDb(fen, cursor, 'indiv', ('public',),
                            'id=?', (1, row[0]))
    return


def ToolsPrivatePublicWedding(fen, cursor, date):
    """ if wedding 80 years old => datas are public
    input:
        fen     : pointer to window
        cursor  : pointer to database
    output:
        nothing
    """
    rows = SelectTabDb(fen, cursor, 'indiv', ('*',),
                       'null', 0, 1, 'null')
    if rows:
        for row in rows:
            event = SelectTabDb(fen, cursor, 'event', ('year',),
                                '(idh=? OR idw=?) AND type=?',
                                (row[0], row[0], 'MARR'), 0, 'null')
            if event:
                if event[0]:
                    if date.year - int(event[0]) > 79:
                        UpdateTabDb(fen, cursor, 'indiv', ('public',),
                                    'id=?', (1, row[0]))
    return


def ToolsAnalysis(fen):
    """
    analyse the database
    input:
        fen     : pointer to window
    outout:
        nothing
    """
    """ Open the database """
    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    """ check individuals without parents, child and spouse """
    """ check individuals without parents """
    param = ('id', 'name', 'firstname', 'sexe')
    fen.Message(fen.mess["ana00"])
    value = (None, None)
    rows = SelectTabDb(fen, cursor, 'indiv', param,
                       'idfather IS ? AND idmother IS ?',
                       value, 1, 'null')

    if rows:
        for row in rows:
            """ Check if individual as child """
            if row[3] == 'M':
                child = SelectTabDb(fen, cursor, 'indiv', ('*',), 'idfather=?',
                                    (row[0],), 1, 'null')
            else:
                child = SelectTabDb(fen, cursor, 'indiv', ('*',), 'idmother=?',
                                    (row[0],), 1, 'null')
            if not child:
                """ Check if individual as spouse """
                spous = SelectTabDb(fen, cursor, 'fam', ('*',),
                                    'idh=? OR idw=?', (row[0], row[0]),
                                    1, 'null')
                if not spous:
                    fen.Message("%04d %s %s" % (row[0], row[1], row[2]))

    """ select individuals over 99 years old and still alive """
    fen.Message(fen.mess["ana01"])
    date = datetime.datetime.now()
    year = date.year
    rows = SelectTabDb(fen, cursor, 'indiv', param, 'null', 0, 1, 'null')
    if rows:
        for row in rows:
            data = SelectTabDb(fen, cursor, 'event', ('*',),
                               '(idh=? or idw=?) AND type=?',
                               (row[0], row[0], 'DEAT'), 0, 'null')
            if not data:
                birth = SelectTabDb(fen, cursor, 'event', ('year',),
                                    '(idh=? or idw=?) AND type=?',
                                    (row[0], row[0], 'BIRT'), 0, 'null')
                if birth:
                    if birth[0]:
                        age = year - int(birth[0])
                        if age > 99:
                            fen.Message("%04d %-20s %-25s : %s %04d (%04d)" %
                                        (row[0], row[1], row[2], fen.mess["ana02"],
                                         int(birth[0]), age))
    return
