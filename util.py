""" Definition of utilities
 Author                        : Ph OCONTE
 Date                          : november 26, 2021
 Date of last update           : november 28, 2021
 Version                       : 1.0.0
"""
import os
import datetime
from PyQt5.QtWidgets import (QFileDialog, QMessageBox, QDialogButtonBox)

from shutil import copyfile

from dbmanagment import SelectTabDb, CountTabDb, LinkDb
from reference import dateap_gb


def ReadFile(fen, mes1, mes2, type, mes3, dir):
    """
    Request file for reading
    input:
        fen     : pointer to window
        mes1    :
        mes2    :
        type    : type of file
        mes3    :
        dir     : working directory
    output:
        file[0] : name of the file
    """

    file = QFileDialog.getOpenFileName(fen, mes2, dir, type)

    file_name = os.path.basename(file[0])
    fen.Message("%s : %s" % (mes1, file_name))

    return file[0]


def WriteFile(fen, mes1, mes2, type, mes3, dir):
    """
    Request file for writing
    input:
        fen     : pointer to window
        mes1    :
        mes2    :
        type    : type of file
        mes3    :
        dir     : working directory
    output:
        file[0] : file name
    """
    file = ""
    file = QFileDialog.getSaveFileName(fen, mes2, dir, type)
    if not file[0]:
        return ''

    file_name = os.path.basename(file[0])
    file_dir = os.path.dirname(file[0])
    ext = file_name.split('.')
    if len(ext) < 2:
        file_name = "%s%s" % (file_name, type[1:])
        file_com = "%s/%s" % (file_dir, file_name)
        fen.Message("%s : %s" % (mes1, file_name))
        return(file_com)

    fen.Message("%s : %s" % (mes1, file_name))

    return (file[0])


def CopyFile(fen):
    """ Copy file
    input:
        fen     : pointer to window
    output:
        nothing
    """
    date = datetime.datetime.now()
    date_s = "%04d%02d%02d%02d%02d%02d" % (date.year, date.month, date.day,
                                           date.hour, date.minute, date.second)
    source = LinkDb(fen)
    if source:
        if os.path.exists(source):
            destination = ('.').join(source.split('.')[:-1])
            destination = "%s_%s.%s" % (destination, date_s, source.split('.')[-1])
            copyfile(source, destination)

    return


def InitList(fen, cursor):
    """
    Init the list of individuals
    input:
        fen     : pointer to window
        cursor  : pointer to database
    output:
        nothing
    """
    param = ('id', 'name', 'firstname')
    rows = SelectTabDb(fen, cursor, 'indiv', param, 'null', 0, 1,
                       'ORDER BY name, firstname')
    nb = CountTabDb(fen, cursor, 'indiv')
    fen.Message("%s %05d" % (fen.mess["all00"], nb[0]))
    if rows:
        data = []
        fen.IndivList.clear()
        for row in rows:
            data.append("%4s %s %s" % (row[0], row[1], row[2]))
        SelList(data, fen.IndivList, 0)
    return


def SelList(list, case, flag):
    """
    Init ComboBox
    Inout:
        list    : data to write
        case    : ComboBox
        flag    : 1 => insert empty row
    output:
        nothing
    """
    """ Clear ComboBox """
    case.clear()

    """ Insert data to ComboBox """
    if flag == 1:
        case.insertItem(0, '')
    i = flag
    for lst in list:
        case.insertItem(i, lst)
        i += 1

    return


def ReadEventSexe(fen, id, sexe, type, cursor):
    """
    Selecting an event based on gender
    input:
        fen     : pointer to window
        sexe    : individual sexe
        type    : type of event
        cursor  : pointer to database
    output:
        data    : data of event
    """
    param = ('day', 'month', 'year', 'city', 'note', 'com1',
             'source', 'time', 'precision', 'id')
    if sexe == 'M':
        cond1 = 'idh=? AND type=?'
    else:
        cond1 = 'idw=? AND type=?'
    data = SelectTabDb(fen, cursor, 'event', param, cond1,
                       (id, type), 1, 'null')
    return data

def utilTreeClear(fen):
    """
    Clear the tree
    input:
        fen     : pointer to window
    output:
        nothing
    """
    datas = ('PaternelGrandFather', 'PaternelGrandMother', 'MaternelGrandFather',
             'MaternelGrandMother', 'Father', 'Mother', 'Individual',
             'Spouse', 'Children', 'BrothersandSisters')
    for data in datas:
        getattr(fen, data).clear()
    return

def DateExplode(date, month_lg):
    """ Transform date dd/mm/yyyy to dd/month/year
    input:
        date        : date to explode
        month_lg    : month in the selected language
    output:
        date
    """
    data = [None, None, None, 0]
    ldate = date.split(' ')
    i = 0
    if ldate[i] in dateap_gb:
        data[3] = dateap_gb.index(ldate[i])
        i += 1
    if len(ldate) == i + 3:         # day, month, year
        data[0] = ldate[i]
        if ldate[i + 1] in month_lg:
            data[1] = 1 + month_lg.index(ldate[i + 1])
        data[2] = ldate[i + 2]
    if len(ldate) == i + 2:         # month, year
        if ldate[i] in month_lg:
            data[1] = 1 + month_lg.index(ldate[i])
        data[2] = ldate[i + 1]
    if len(ldate) == i + 1:         # year
        data[2] = ldate[i]

    return(data)
