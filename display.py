""" Display the data from database
 Author                        : Ph OCONTE
 Date                          : november 27, 2021
 Date of last update           : november 27, 2021
 Version                       : 1.0.0
"""
import sqlite3
import datetime
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QPixmap

from dbmanagment import LinkDb, DefDb
from util import InitList

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
    # nb = CountTabDb(fen, cursor, 'fam')
    # fen.Message("%s %05d" % (fen.mess["all02"], nb[0]))
    """ Count the number of events """
    # nb = CountTabDb(fen, cursor, 'event')
    # fen.Message("%s %05d" % (fen.mess["all01"], nb[0]))
    """ Count the number of objects """
    # nb = CountTabDb(fen, cursor, 'object')
    # fen.Message("%s %05d" % (fen.mess["all04"], nb[0]))

    conn.commit()
    cursor.close()
    conn.close()

    return
