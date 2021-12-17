"""
Read and write CSF file
Author                        : Ph OCONTE
Date                          : december 17, 2021
Date of last update           : december 17, 2021
Version                       : 1.0.0

Family tab format
c0 : Id
c1 : Generation level
c2 : Name of individual
c3 : First name of individual
c4 : sexe
c5 : job
birth   wedding     death
c6 : day    c12: day    c19: day
c7 : month  c13: month  c20: month
c8 : year   c14: year   c21: year
c9 : city   c15: city   c22: city
c10: note   c16: note   c23: note
c11: source c17: source c24: source
            c18: age    c25: age
c26: age
c27: father id
c28: name of the father
c29: first name of the father
c30: mother id
c31: name ofn the mother
c32: first name of the mother
c33: spouse id
c34: name of the spouse
c35: first name of the spouse

City tab format
c0 : locality
c1 : city
c2 : insee code
c3 : postal code
c4 : department
c5 : district
c6 : country
"""
import sqlite3
import datetime

from util import ReadFile, WriteFile, InitList
from dbmanagment import ResetDb, LinkDb, SelectTabDb, InsertTabDb
from dbmanagment import UpdateTabDb
from reference import event_gb

"""     Family csv file header """
lin1ent1 = "Id;Level;Name;First name;Sexe;Job;Birth;;;;;;Wedding;;;;;;;"
lin1ent2 = "Death;;;;;;;Age;Father;;;Mother;;;Spouse;;"
lin2ent1 = ";;;;;;D/M/Y;;;City;Note;Source;D/M/Y;;;City;Note;Source;Age;"
lin2ent2 = "D/M/Y;;;City;Note;Source;Age;;Id;Name;First name;Id;Name;First name;"
lin2ent3 = "Id;Name;First name"

""" City csv file header """
line1entCity = "Loaclity;city;Insee code;Postal code;Department:District;Country"

def CsvRead(fen):
    """
    reading family and community csv files
    input :
        fen : pointer to window
    output:
        nothing
    """
    fen.Message(fen.mess["csv00"])
    """ Finding the CSV file of families to read """
    fam = ReadFile(fen, fen.mess["csv01"], fen.mess["csv05"], "*.csv",
                      fen.mess["all06"], fen.WorkingDirectory)
    if not fam:
        return

    """ Finding the CSV file of cities to read """
    cit = ReadFile(fen, fen.mess["csv02"], fen.mess["csv06"], "*.csv",
                      fen.mess["all06"], fen.WorkingDirectory)
    if not cit:
        return

    """ Open, read, then close the CSV file of families """
    readfile = open(fam, "r")
    lines = readfile.readlines()
    readfile.close()

    """ if the database is already initialized, reset it """
    ResetDb(fen)

    """ Open the database """
    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    fen.Message(fen.mess["csv03"])
    Nbid = 0
    Nbfam = 1
    Nbeven = 0

    for line in lines:
        """ Initialize the list of individuals """
        lin = line.split(';')
        if lin[1].isdigit():
            Nbid += SaveIndi(fen, conn, cursor, lin[0].strip(), lin[2].strip(),
                             lin[3].strip(), lin[4].strip(), lin[27].strip(),
                             lin[30].strip())
            """ save the job """
            Nbeven += CsvInsertEvent(fen, conn, cursor, lin[0], "OCCU", "", "", "",
                                     "", "", "", lin[5], "", "", "", "")

            event = ('BIRT', 'MARR', 'DEAT')
            j = 0
            x = (6, 12, 19)
            for i in x:      # BIRT, MARR, DEAT
                Nbeven += CsvInsertEvent(fen, conn, cursor, lin[0], event[j], lin[4].strip(),
                                         lin[i], lin[i+1], lin[i+2], lin[i+3], lin[i+4],
                                         lin[i+5], "", "", "", "")
                j += 1

            """ Save families """
            if len(lin[33]) > 0:
                Nbfam += SaveFam(fen, conn, cursor, lin[0], lin[33], lin[4],
                                 Nbfam)
            if len(lin[28]) > 0 or len(lin[31]) > 0:
                Nbfam += SaveFam(fen, conn, cursor, lin[27], lin[30], 'M',
                                 Nbfam)


    """ Display the number of individuals """
    fen.Message("\t%s %05d" % (fen.mess["all00"], Nbid))
    """ Display the number of families """
    fen.Message("\t%s %05d" % (fen.mess["all02"], Nbfam - 1))
    """ Display the number of events """
    fen.Message("\t%s %05d" % (fen.mess["all01"], Nbeven))

    """ Open, read, then close the CSV file of cities """
    readfile = open(cit, "r")
    lines = readfile.readlines()
    readfile.close()

    fen.Message(fen.mess["csv04"])
    Nbcom = 0
    locality = ""
    for line in lines:
        lin = line.split(';')
        if not (lin[0] == "City") and not (lin[0] == "Ville"):
            param = ('locality', 'city', 'Insee', 'Postal', 'dep',
                     'district', 'country')
            values = (locality, lin[0], lin[1],  lin[2], lin[3],
                      lin[4], lin[5][:-1])
            InsertTabDb(fen, cursor, 'city', param, values)
            Nbcom += 1
    conn.commit()
    fen.Message("\t%s %05d" % (fen.mess["all03"], Nbcom))

    """ Substitution of the names of the cities by the long form """
    SubsCom(fen, cursor)
    conn.commit()
    InitList(fen, cursor)

    cursor.close()
    conn.close()
    fen.Message(fen.mess["all44"])
    return


def SaveIndi(fen, conn, cursor, id, name, firstname, sexe, idfather, idmother):
    """
    Check if the individual is already registered
    input :
        fen       : pointer to window
        conn      : link to database
        cursor    : pointer to database
        id        : individual id
        name      : name of the individual
        firstname : first name of the individual
        sexe      : sexe of the individual
        idfather  : father id
        idmother  : mother id
    output:
        0      : the individual already exists
        1      : the individual is created
    """
    params = ('name', 'firstname', 'sexe', 'idfather', 'idmother', 'public')
    indiv = SelectTabDb(fen, cursor, 'indiv', params, 'id=?',
                        (id,), 0, 'null')
    if indiv:
        return 0
    """ Initialization of the individual """
    pers = [None, None, None, None, None, None, 0]
    pers[0] = id
    if len(name) > 0:
        pers[1] = name
    if len(firstname) > 0:
        pers[2] = firstname
    if sexe != 'M' and sexe != 'F':
        sexe = '?'
    pers[3] = sexe
    """ the father is known """
    if idfather.isdigit():
        pers[4] = idfather
    """ the mother is known """
    if idmother.isdigit():
        pers[5] = idmother
    params = ('id', 'name', 'firstname', 'sexe', 'idfather',
              'idmother', 'public')
    InsertTabDb(fen, cursor, 'indiv', params, pers)
    return 1


def SaveFam(fen, conn, cursor, id1, id2, sexe, Nbfam):
    """
    Definition of a family
    input:
        fen     : pointer to window
        conn    : link to database
        cursor  : pointer to database
        id1     : individual id
        id2     : spouse id
        sexe    : sexe of the indivdual
        Nbfam   : number of families
    output:
        0       : the family already exists
        1       : the family is created
    """
    """ Check if the family already exists """
    if sexe == 'M':
        idh, idw = id1, id2
    else:
        idh, idw = id2, id1

    famx = SelectTabDb(fen, cursor, 'fam', ('id',), 'idh=? AND idw=?',
                       (idh, idw), 0, 'null')
    """ If the family already exists return 0 """
    if famx:
        return 0

    """ Save the family """
    values = [None, None, None]
    values[0] = Nbfam
    if idh:
        values[1] = (idh)
    if idw:
        values[2] = (idw)
    InsertTabDb(fen, cursor, 'fam', ('id', 'idh', 'idw'), values)
    return 1


def SubsCom(fen, cursor):
    """
    Substitution of cities by the long form
    input:
        fen     : pointer to window
        cursor  : pointer to database
    output:
        nothing
    """

    param = ('locality', 'city', 'Insee', 'Postal',
             'dep', 'district', 'country')
    rows = SelectTabDb(fen, cursor, 'city', param, 'null', (0),
                       1, 'null')
    for row in rows:
        city = ','.join(row)
        params = ('city',)
        values = (city, row[1])
        UpdateTabDb(fen, cursor, 'event', params, 'city=?', values)
    return


def CsvWrite(fen):
    """
    Write families and cities CSV files
    input :
        fen     : pointer to window
    output:
        nothing
    """
    fen.Message(fen.mess["csv07"])
    """ Ask the CSV families file name """
    fam = WriteFile(fen, fen.mess["csv10"], fen.mess["csv08"], "*.csv",
                    fen.mess["all07"], fen.WorkingDirectory)
    if not fam:
        return

    """ Ask the CSV cities file name """
    cit = WriteFile(fen, fen.mess["csv11"], fen.mess["csv09"], "*.csv",
                    fen.mess["all07"], fen.WorkingDirectory)
    if not cit:
        return

    """ Open the files to write """
    fam_wri = open(fam, "w")
    if not fam_wri:
        return
    cit_wri = open(cit, "w")
    if not cit_wri:
        return

    """ Ecriture de l'entête du fichier """
    fam_wri.write("%s%s\n" % (lin1ent1, lin1ent2))
    fam_wri.write("%s%s%s\n" % (lin2ent1, lin2ent2, lin2ent3))

    """ Open the database """
    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    """ Write the individuals """
    params = ('*')
    rows = SelectTabDb(fen, cursor, 'indiv', params, 'null', 0, 1,
                       'ORDER BY name, firstname')
    for row in rows:
        nais_age = 0
        dec_age = 0
        """ id, level, name, firstname, sexe """
        """ Value none for level """
        fam_wri.write("%s;;%s;%s;%s;" % (row[0], row[1], row[2], row[3]))
        """ Voir si metier """
        data = EventWrite(fen, cursor, row[0], "OCCU")
        if data[9] == "1":
            fam_wri.write("%s;" % (data[6]))
        else:
            fam_wri.write(";")
        """ Naissance """
        data = EventWrite(fen, cursor, row[0], "BIRT")
        if data[9] == "1":
            if len(data[2]) > 3:            # birth after 1000
                nais_age = int(data[2])
            else:
                nais_age = 0
            fam_wri.write("%s;%s;%s;%s;%s;%s;" % (data[0], data[1],
                          data[2], data[3], data[4], data[5]))
        else:
            fam_wri.write(";;;;;;")
        """ Mariage """
        data = EventWrite(fen, cursor, row[0], "MARR")
        if data[9] == "1":
            if len(data[2]) > 3 and nais_age != 0:
                mar_age = "%s" % (int(data[2]) - nais_age)
            else:
                mar_age = ""
            fam_wri.write("%s;%s;%s;%s;%s;%s;%s;" % (data[0],
                          data[1], data[2], data[3], data[4], data[5],
                          mar_age))
        else:
            fam_wri.write(";;;;;;;")
        """ Décès """
        data = EventWrite(fen, cursor, row[0], "DEAT")
        if data[9] == "1":
            if len(data[2]) > 3 and nais_age != 0:
                dec_age = "%s" % (int(data[2]) - nais_age)
            else:
                dec_age = ""
            fam_wri.write("%s;%s;%s;%s;%s;%s;%s;" % (data[0], data[1],
                          data[2], data[3], data[4], data[5], dec_age))
        else:
            fam_wri.write(";;;;;;;")
        """ Age du personnage si toujours vivant """
        if nais_age != 0 and dec_age == "":
            date = datetime.datetime.now()
            act_age = date.year - nais_age
            fam_wri.write("%s;" % (act_age))
        else:
            fam_wri.write(";")
        """ Search father """
        ParentWrite(fen, cursor, row[4], fam_wri)
        """ Search mother """
        ParentWrite(fen, cursor, row[5], fam_wri)
        """ Search spouse """
        SpouseWrite(fen, cursor, row[0], row[3], fam_wri)

        fam_wri.write("\n")

    fam_wri.close()

    """ Save the CSV cities file """
    CitiesSave(fen, cursor, cit_wri)
    cit_wri.close()

    cursor.close()
    conn.close()
    fen.Message(fen.mess["all44"])
    return


def EventWrite(fen, cursor, indiv, type):
    """
    Write event
    input:
        fen     : pointer to window
        cursor  : pointer to database
        indiv   : id of individual
        type    : type event
    output:
        data    : data of event
    """
    data = ["", "", "", "", "", "", "", "", "", "0"]
    params = ('day', 'month', 'year', 'city', 'note', 'source',
              'com1', 'com2', 'com3')
    values = (type, indiv, indiv)
    eventw = SelectTabDb(fen, cursor, 'event', params,
                         'type=? AND (idh=? OR idw=?)',
                         values, 0, 'null')
    if eventw:
        for i in range(0, 9):
            if eventw[i]:
                data[i] = "%s" % (eventw[i])
        if eventw[3]:
            city = eventw[3].split(',')
            data[3] = city[1]
        data[9] = "1"
    return data


def ParentWrite(fen, cursor, id, fam_wri):
    """
    Search parent name and firstname
    input:
        fen     : pointer to window
        cursor  : pointer to database
        id      : id of individual
        fam_wri : write file
    output:
        nothing
    """

    if id:
        params = ('name', 'firstname')
        par = SelectTabDb(fen, cursor, 'indiv', params, 'id=?',
                          (id,), 0, 'null')
        if par:
            fam_wri.write("%s;%s;%s;" % (id, par[0], par[1]))
            return

    fam_wri.write(";;;")
    return


def SpouseWrite(fen, cursor, id, sexe, fam_wri):
    """
    Search spouse
    input:
        fen     : pointer to window
        cursor  : pointer to database
        id      ; id of individual
        sexe    : sexe du personnage
        fam_wri : file to write
    output:
        nothing
    """
    if sexe == 'M':
        spo = SelectTabDb(fen, cursor, 'fam', ('idw',), 'idh=?',
                          (id,), 0, 'null')
    else:
        spo = SelectTabDb(fen, cursor, 'fam', ('idh',), 'idw=?',
                          (id,), 0, 'null')
    if spo:
        if spo[0]:
            params = ('name', 'firstname')
            spox = SelectTabDb(fen, cursor, 'indiv', params, 'id=?',
                               (spo[0],), 0, 'null')
            if spox:
                fam_wri.write("%s;%s;%s" % (spo[0], spox[0], spox[1]))
                return

    fam_wri.write(";;")
    return


def CitiesSave(fen, cursor, cit_wri):
    """
    Save the CSV cities file
    input:
        fen     : pointer to window
        cursor  : pointer to database
        cit_wri : CSV cities file
    output:
        nothing
    """

    params = ('locality', 'city', 'Insee', 'Postal', 'dep',
              'district', 'country')
    rows = SelectTabDb(fen, cursor, 'city', params, 'null', 0,
                       1, 'ORDER BY city')
    cit_wri.write("%s\n" % (line1entCity))
    for row in rows:
        data = ["", "", "", "", "", "", ""]
        for i in range(0, 7):
            if row[i] is not None:
                data[i] = row[i]
                if i == 2 and row[i].isnumeric():
                    data[2] = "%05d" % (int(row[2]))
                if i == 3 and row[i].isnumeric():
                    data[3] = "%05d" % (int(row[3]))
        cit_wri.write("%s;%s;%s;%s;%s;%s;%s\n" % (data[0], data[1],
                      data[2], data[3], data[4], data[5], data[6]))
    return


def CsvInsertEvent(fen, conn, cursor, indiv, type, sexe, day, month,
                   year, city, note, source, com1, com2, com3, spouse):
    """
    Insert an event
    input:
        fen     : pointer towindow
        conn    : link to database
        cursor  : poiter to database
        indiv   : individual id
        type    : event type
        sexe    : sexe of individual
        day     : day of event
        month   : month of event
        year    : year of event
        city    : city of event
        note    : note of event
        source  : origin of the information
        com1    : additional information
        com2    : not used
        com3    : not used
        spouse  : in the case of marriage or divorce name of spouse
    output:
        0       : the event already exists
        1       : the event is created
    """

    if len(day) == 0 and len(month) == 0 and len(year) == 0\
        and len(city) == 0 and len(note) == 0 and len(source) == 0\
        and len(com1) == 0 and len(com2) == 0 and len(com3) == 0\
        and len(spouse) == 0:
        return 0

    """ Check if the event is already registered """
    if type in event_gb:
        params = ('day', 'month', 'year', 'city', 'note', 'com1',
                  'source', 'precision', 'time', 'idh', 'idw')
        values = (indiv, indiv, type)
        event = SelectTabDb(fen, cursor, 'event', params,
                            '(idh=? OR idw=?) AND type=?',
                            values, 0, 'null')
        if event:
            return 0

    """ register the event """
    eve = [None, None, None, None, None, None, None, None, None, None, 0]
    if type == 'MARR' or type == 'DIV':
        if sexe == 'M':
            eve[0], eve[1] = indiv, spouse
        else:
            eve[0], eve[1] = spouse, indiv
    else:
        eve[0], eve[1] = indiv, indiv
        eve[2] = type
    """ date analysis """
    if len(day) > 0:
        eve[3] = int(day)
    if len(month) > 0:
        eve[4] = int(month)
    if len(year) > 0:
        eve[5] = int(year)
    if len(city) > 0:
        eve[6] = city
    if len(note) > 0:
        eve[7] = note
    if len(source) > 0:
        eve[8] = source
    if len(com1) > 0:
        eve[9] = com1
    params = ('idh', 'idw', 'type', 'day', 'month', 'year',
              'city', 'note', 'source', 'com1', 'precision')
    InsertTabDb(fen, cursor, 'event', params, eve)
    return 1
