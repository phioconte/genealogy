""" Open an existing database
    Author                        : Ph OCONTE
    Date                          : november 27, 2021
    Last date of update           : november 29, 2021
    Version                       : 1.0.0

    In the config.txt file update the name of the database
    and read this new database
"""
import os

from util import ReadFile, WriteFile
from display import DisplayIn
from config import ConfigSaveUpdate
from dbmanagment import LinkDb

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


def RenameDb(fen):
    """
    Rename the database
    input:
        fen     : pointer to window
    output:
        nothing
    """

    """ Ask the new name of the database """
    destination = WriteFile(fen, fen.mess["all43"], "mes2", '*.db', "mes3",
                            fen.WorkingDirectory)

    if not destination:
        return

    """ Source file """
    source = LinkDb(fen)

    """ Rename file """
    os.rename(source, destination)

    """ Save the new name in config.txt file """
    ConfigSaveUpdate(fen, destination)
    return
