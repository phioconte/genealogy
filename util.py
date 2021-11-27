""" Definition of utilities
 Author                        : Ph OCONTE
 Date                          : november 26, 2021
 Date of last update           : november 26, 2021
 Version                       : 1.0.0
"""
import os
from PyQt5.QtWidgets import (QFileDialog, QMessageBox, QDialogButtonBox)

from dbmanagment import SelectTabDb, CountTabDb

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
        showDialog(mes2, mes3)
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
