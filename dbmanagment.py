""" Definition of database access utilities
 Author                        : Ph OCONTE
 Date                          : november 26, 2021
 Date of last update           : november 26, 2021
 Version                       : 1.0.0
"""
import os
import sqlite3


def LinkDb(fen):
    """ Define the link to database
    input:
        fen     : pointer to window
    output:
        data    : link to database
    """
    data = None
    if fen.WorkingDirectory and fen.Database:
        data = os.path.join(fen.WorkingDirectory, fen.Database)

    return data


def DefDb(fen, conn, cursor):
    """
    Creation of individuals, events, families, objects and cities tables,
    input:
        fen     : pointer to window
        conn    : link to database
        cursor  : pointer to database
    output:
        nothing
    """
    fen.Message(fen.mess["all05"])

    """ Creation of the individuals table if it does not exist"""
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS indiv(
            id INTEGER, name TEXT, firstname TEXT, sexe TEXT,
            idfather INTEGER, idmother INTEGER, public INTEGER)""")
    conn.commit()

    """ Creation of the events table if it does not exist """
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS event(
            id INTEGER PRIMARY KEY AUTOINCREMENT, idh INTEGER, idw INTEGER,
            type TEXT, day integer, month INTEGER, year INTEGER,
            city TEXT, note TEXT, com1 TEXT, com2 TEXT, com3 TEXT,
            source TEXT, precision TEXT, time TEXT)""")
    conn.commit()

    """ Creation of the families table if it does not exist """
    cursor.execute(
            """CREATE TABLE IF NOT EXISTS fam(
            id INTEGER, idh INTEGER,
            idw INTEGER)""")
    conn.commit()

    """ Creation of the object table if it does not exist """
    cursor.execute(
            """ CREATE TABLE IF NOT EXISTS object(
            id INTEGER PRIMARY KEY AUTOINCREMENT, idobj INTEGER,
            indiv INTEGER, file TEXT, form TEXT, title TEXT)""")
    conn.commit()

    """ Creation of the cities table if it does not exist"""
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS city(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, locality TEXT,
            city TEXT, Insee TEXT, Postal TEXT, dep TEXT, district TEXT,
            country TEXT)""")
    conn.commit()

    return


def ResetDb(fen):
    """
    Delete the database file if it exists
    input:
        fen     : pointer to window
    output:
        nothing
    """
    if os.path.exists(LinkDb(fen)):
        os.remove(LinkDb(fen))

    """ Create the database """
    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    DefDb(fen, conn, cursor)

    conn.commit()
    cursor.close()
    conn.close()

    return


def SelectTabDb(fen, cursor, table, params, cond1, values, flag, cond2):
    """
    Data selection
    input:
        fen     : pointer to window
        cursor  : pointer to database
        table   : Table to read
        params  : Column to select
        cond1   : Selection condition
        values  : values
        flag    : 0 => fetchone, 1 => fetchall
        cond2   : Sort condition
    output:
        read data
    """
    sql = 'SELECT '
    for par in params:
        sql = '%s %s,' % (sql, par)
    sql = sql[:-1]
    sql = "%s FROM %s" % (sql, table)
    if cond1 != 'null':
        sql = "%s WHERE %s" % (sql, cond1)
        if cond2 != 'null':
            sql = "%s %s" % (sql, cond2)
        cursor.execute(sql, (values))
    else:
        if cond2 != 'null':
            sql = "%s %s" % (sql, cond2)
        cursor.execute(sql)

    if flag == 0:
        data = cursor.fetchone()
    else:
        data = cursor.fetchall()

    return data


def DeleteTabDb(fen, cursor, table, cond, values):
    """
    Delete a record from the table
    input:
        fen     : pointer to window
        cursor  : pointer to database
        table   : Table to read
        cond    : Selection condition
        values  : values
    output:
        nothing
    """

    sql = 'DELETE FROM %s WHERE %s' % (table, cond)
    cursor.execute(sql, (values))
    return


def UpdateTabDb(fen, cursor, table, params, cond, values):
    """
    Update record from the table
    input:
        fen     : pointer to window
        cursor  : pointer to database
        table   : Table to read
        params  : Column to select
        cond    : Selection condition
        values  : values
    output:
        nothing
    """
    sql = 'UPDATE %s SET ' % (table)
    for par in params:
        sql = '%s %s=?,' % (sql, par)
    sql = sql[:-1]
    sql = "%s WHERE %s" % (sql, cond)
    cursor.execute(sql, (values))
    return


def InsertTabDb(fen, cursor, table, params, values):
    """
    Inserting a new record in the table
    input:
        fen     : pointer to window
        conn    : link to database
        cursor  : pointer to database
        table   : table to read
        params  : Column to select
        values  : values
    output:
        return the last id
    """
    sql = "INSERT INTO %s(" % (table)
    for par in params:
        sql = "%s %s," % (sql, par)
    sql = sql[:-1]
    sql = "%s) VALUES(" % (sql)
    for par in params:
        sql = "%s ?," % (sql)
    sql = sql[:-1]
    sql = "%s)" % (sql)
    cursor.execute(sql, values)
    return cursor.lastrowid


def CountTabDb(fen, cursor, table):
    """
    Count the number of items in a table
    input:
        fen     : pointer to window
        cursor  : pointer to database
        table   : table to read
    output:
        return the number of item
    """
    sql = 'SELECT COUNT(*) FROM %s' % (table)
    data = cursor.execute(sql)
    nb = data.fetchone()
    return nb
