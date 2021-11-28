""" Open an existing database
    Author                        : Ph OCONTE
    Date                          : november 27, 2021
    Last date of update           : november 28, 2021
    Version                       : 1.0.0

    In the config.txt file update the name of the database
    and read this new database
"""
import os

from util import ReadFile
from display import DisplayIn
from config import ConfigSaveUpdate

def OpenDatabase(fen):
    """ Select the new database """
    OpenFile = ReadFile(fen, fen.mess["all60"], fen.mess["all61"],
                        "*.db", "mes3", fen.WorkingDirectory)

    fen.Database = os.path.basename(OpenFile)
    """ Update config.txt """
    ConfigSaveUpdate(fen, OpenFile)

    """ Read database """
    DisplayIn(fen)
    return
