"""
Read and write GEDCOM file
Author                        : Ph OCONTE
Date                          : november 28, 2021
Date of last update           : november 28, 2021
Version                       : 1.1.0
"""
import os
import datetime
import sqlite3

from util import ReadFile, WriteFile, InitList, DateExplode
from util import ReadEventSexe, utilTreeClear
from dbmanagment import ResetDb, LinkDb
from dbmanagment import InsertTabDb, UpdateTabDb, SelectTabDb
from reference import event_gb, event_ind, month_gb, dateap_gb

""" GEDCOM file header """
gheader = ("0 HEAD\n",
           "  1 NOTE This file was created by python software\n",
           "  1 GEDC\n",
           "    2 FORM LINEAGE - LINKED\n",
           "    2 VERS 5.5.1\n",
           "  1 PLAC\n",
           "    2 FORM Lieudit, Commune, Code_INSEE, Code_Postal, Département, Région, Pays\n",
           "  1 SOUR Python CSV to GED\n",
           "    2 VERS 1.0.0\n",
           "    2 NAME genealogy python\n",
           "    2 CORP OCONTE TEAM\n",
           "  1 DEST ANY\n")


def GedcomRead(fen):
    """
    Read GEDCOM file
    input:
        fen     : pointer to window
    output:
        nothing
    """
    fen.Message(fen.mess["ged12"])

    """ Ask the file to read """
    gedr = ReadFile(fen, fen.mess["ged14"], fen.mess["ged13"], "*.ged",
                    fen.mess["all06"], fen.WorkingDirectory)

    """ If no file selected, indicate it then return """
    if not gedr:
        return

    """ Read and close the GEDCOM file """
    readfile = open(gedr, "r")
    lines = readfile.readlines()
    readfile.close()
    Nb = [0, 0, 0]
    Nbfam = 0
    Nbsou = 0

    """ If the database is already initialized, reset it """
    ResetDb(fen)

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    data = []
    for line in lines:
        line = line.strip()
        lin = line.split(' ')
        if lin[0] == '0':
            if data and (len(data[0]) > 2 or lin[1] == 'TRLR'):
                if data[0][2] == 'INDI':                # individu
                    Nbret = GedcomReadIndi(fen, data, cursor)
                    Nb[0] += Nbret[0]
                    Nb[1] += Nbret[1]
                    Nb[2] += Nbret[2]
                if data[0][2] == 'FAM':                 # famille
                    Nbret = GedcomReadFam(fen, data, cursor)
                    Nbfam += Nbret[0]
                    Nb[1] += Nbret[1]
                if data[0][2] == 'OBJE':                # objet
                    Nb[2] += GedcomReadObj(fen, data, cursor)
                if data[0][2] == 'SOUR':                # source
                    Nbsou += GedcomReadSource(fen, data, cursor)
            data[:] = []
        data.append(lin)

    fen.Message("%s %05d" % (fen.mess["all00"], Nb[0]))
    fen.Message("%s %05d" % (fen.mess["all01"], Nb[1]))
    fen.Message("%s %05d" % (fen.mess["all04"], Nb[2]))
    fen.Message("%s %05d" % (fen.mess["all02"], Nbfam))
    fen.Message("%s %05d" % (fen.mess["all12"], Nbsou))

    conn.commit()
    """ Add individuals to the list """
    InitList(fen, cursor)

    """ Extract the cities and save its in city table """
    ExtractCity(fen, cursor)
    conn.commit()

    cursor.close()
    conn.close()
    utilTreeClear(fen)
    fen.Message(fen.mess["all44"])
    return


def GedcomReadIndi(fen, data, cursor):
    """
    Read individual
    input:
        fen     : pointer to window
        data    :
        cursor  : pointer to database
    output:
        retind  : counting of individuals, events and objects
    """
    retind = [0, 0, 0]
    """ Extract individual id """
    id = data[0][1][2:-1]
    """ Check if the individual already exists in the database """
    row = SelectTabDb(fen, cursor, 'indiv', ('*',), 'id=?',
                      (id,), 0, 'null')
    if row:
        return retind
    """ Insert the new individual """
    retind[0] = 1
    param = ('id', 'public')
    InsertTabDb(fen, cursor, 'indiv', param, (id, 1))
    for pt in range(1, len(data)):
        if data[pt][0] == '1':
            if data[pt][1] == 'NAME':
                firstnamename = (' '.join(data[pt][2:])).strip()
                namep = firstnamename.split('/')
                name = '?'
                firstname = '?'
                if len(namep) == 1:
                    firstname = namep[0].strip()
                if len(namep) > 1:
                    firstname = namep[0].strip()
                    name = namep[1].strip()
                param = ('name', 'firstname')
                value = (name, firstname, id)
                UpdateTabDb(fen, cursor, 'indiv', param, 'id=?',
                            value)

            if data[pt][1] == 'SEX' and len(data[pt]) > 2:
                param = ('sexe',)
                value = (data[pt][2], id)
                UpdateTabDb(fen, cursor, 'indiv', param, 'id=?',
                            value)

            if data[pt][1] in event_gb:
                retind[1] += GedcomReadEvent(fen, id, id, data, pt, cursor)

            if data[pt][1] == 'OBJE':
                """
                Check if the object exists,
                    if yes update the individual
                    if not create the object
                """
                if len(data[pt]) > 2:
                    obj = data[pt][2][2:-1]
                    row = SelectTabDb(fen, cursor, 'object', ('idobj',), 'idobj=?',
                                      ('obj',), 0, 'null')
                    if row:
                        UpdateTabDb(fen, cursor, 'object', ('indiv',), 'idobj=?',
                                    (id, obj))
                    else:
                        retind[2] += 1
                        params = ('idobj', 'indiv')
                        InsertTabDb(fen, cursor, 'object', params, (obj, id))
    return retind


def GedcomReadFam(fen, data, cursor):
    """
    Read family
    input:
        fen     : pointer to window
        data    : data about family
        cursor  : pointer to database
    output:
        1       : New family
        Nbeven  : Number of events recorded
    """
    """ Extract id of family """
    fam = data[0][1][2:-1]
    idhl = ""
    idwl = ""
    Nbeven = 0
    InsertTabDb(fen, cursor, 'fam', ('id',), (fam,))
    for ptfa in range(1, len(data)):
        if data[ptfa][1] == 'HUSB' and len(data[ptfa]) > 2:
            idhl = int(data[ptfa][2][2:-1])
            UpdateTabDb(fen, cursor, 'fam', ('idh',), 'id=?',
                        (idhl, fam))
        if data[ptfa][1] == 'WIFE' and len(data[ptfa]) > 2:
            idwl = int(data[ptfa][2][2:-1])
            UpdateTabDb(fen, cursor, 'fam', ('idw',), 'id=?',
                        (idwl, fam))
        if data[ptfa][1] == 'MARR':
            Nbeven += GedcomReadEvent(fen, idhl, idwl, data, ptfa, cursor)
        if data[ptfa][1] == 'CHIL':
            """ Init father and mother """
            chl = int(data[ptfa][2][2:-1])
            if idhl:
                UpdateTabDb(fen, cursor, 'indiv', ('idfather',), 'id=?',
                            (idhl, chl))
            if idwl:
                UpdateTabDb(fen, cursor, 'indiv', ('idmother',), 'id=?',
                            (idwl, chl))
    return [1, Nbeven]


def GedcomReadObj(fen, data, cursor):
    """
    read an object
    input:
        fen     : pointer to window
        data    : object data
        cursor  : pointer to database
    output:
        nbobj   : number objects
    """
    obj = data[0][1][2:-1]
    nbobj = 0
    """ Check if object exists """
    row = SelectTabDb(fen, cursor, 'object', ('*'), 'idobj=?',
                      (obj,), 0, 'null')
    if not row:
        InsertTabDb(fen, cursor, 'object', ('idobj'), (obj))
        nbobj = 1
    for pto in range(1, len(data)):
        if data[pto][1] == 'FILE' and len(data[pto]) > 2:
            file = ' '.join(data[pto][2:])
            UpdateTabDb(fen, cursor, 'object', ('file',), 'idobj=?',
                        (file, obj))
        if data[pto][1] == 'FORM' and len(data[pto]) > 2:
            form = ' '.join(data[pto][2:])
            UpdateTabDb(fen, cursor, 'object', ('form',), 'idobj=?',
                        (form, obj))
        if data[pto][1] == 'TITL' and len(data[pto]) > 2:
            titre = ' '.join(data[pto][2:])
            UpdateTabDb(fen, cursor, 'object', ('titre',), 'idobj=?',
                        (titre, obj))

    return nbobj


def GedcomReadSource(fen, data, cursor):
    """
    Read source
    input:
        fen     : pointer to window
        data    : source data
        cursor  : pointer to database
    output:
        0       : unknown source
        1       : record source
    """
    """ identify the source """
    idsour = data[0][1][2:-1]
    data = ' '.join(data[1][2:])
    """ Find if source and replace it with the designation """
    row = SelectTabDb(fen, cursor, 'event', ('id',), 'source=?',
                      (int(idsour),), 0, 'null')
    if row:
        UpdateTabDb(fen, cursor, 'event', ('source',), 'id=?',
                    (data, row[0]))
        return 1

    return 0


def GedcomReadEvent(fen, id1, id2, data, pt, cursor):
    """
    read event
    input:
        fen     : pointe to window
        id1     : main individual id
        id2     : spouse id
        data    : data of event
        pt      : pointer to event
        cursor  : pointer to database
    output:
        0       : l'évènement existe
        1       : création de l'évènement
    """
    """ Create the l'event """
    event = [None, None, None, None, None, None, None, None,
             None, None, None, None]
    event[0] = id1           # idh
    event[1] = id2           # idw
    event[2] = data[pt][1]   # type

    """ Information """
    if len(data[pt]) > 2:
        event[9] = ' '.join(data[pt][2:])       # com1

    for ptf in range(pt+1, len(data)):
        if data[ptf][0] != '2':
            break
        if data[ptf][1] == 'DATE':
            date = DateExplode(' '.join(data[ptf][2:]), month_gb)
            event[3] = date[0]                   # day
            event[4] = date[1]                   # month
            event[5] = date[2]                   # year
            event[11] = date[3]                  # precision
        if data[ptf][1] == 'PLAC':
            event[6] = ' '.join(data[ptf][2:])   # city
        if data[ptf][1] == 'NOTE':
            event[7] = ' '.join(data[ptf][2:])   # Note
        if data[ptf][1] == 'SOUR':
            event[8] = data[ptf][2][2:-1]        # Source
        if data[ptf][1] == 'TYPE':
            event[9] = ' '.join(data[ptf][2:])   # com1
        if data[ptf][1] == 'TIME':
            event[10] = data[ptf][2]             # time

    """ Sauvegarde de l'évènement """
    params = ('idh', 'idw', 'type', 'day', 'month', 'year', 'city',
              'note', 'source', 'com1', 'time', 'precision')
    InsertTabDb(fen, cursor, 'event', params, event)
    return 1


def ExtractCity(fen, cursor):
    """
    Extract the list of cities
    input:
        fen     : pointer to window
        cursor  : pointer to database
    output:
        nothing
    """
    cities = SelectTabDb(fen, cursor, 'event', ('city',), 'null', 0, 1, 'null')
    Nbcities = 0
    fen.Message(fen.mess["ged17"])
    for city in cities:
        if city[0]:
            cit = city[0].split(',')
            if len(cit) < 7:
                fen.Message("City : %s" % (city[0]))
            else:
                ci = SelectTabDb(fen, cursor, 'city', ('id',), 'city=?',
                                 (cit[1],), 0, 'null')
                if not ci:
                    params = ('locality', 'city', 'Insee', 'Postal',
                              'dep', 'district', 'country')
                    InsertTabDb(fen, cursor, 'city', params, (cit))
                    Nbcities += 1
    fen.Message("%s %s" % (fen.mess["all03"], Nbcities))
    return


def GedcomWrite(fen):
    """
    Write GEDCOM file
    input:
        fen     : pointer to window
    output:
        nothing
    """
    fen.Message(fen.mess["ged00"])
    """ ask the GEDCOM file """
    gedw = WriteFile(fen, fen.mess["ged01"], fen.mess["ged06"], "*.ged",
                     fen.mess["all07"], fen.WorkingDirectory)
    if not gedw:
        return
    """ Open the file to write """
    wri = open(gedw, "w")

    """ Write the header """
    fen.Message(fen.mess["ged02"])
    GedcomHeader(fen, wri, gedw)

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    """ Write all the individuals """
    fen.Message(fen.mess["ged03"])
    data = GedcomWriteIndiv(fen, wri, cursor)

    """ Write all the families """
    fen.Message(fen.mess["ged04"])
    if data:
        nb = data[-1][0]
    else:
        nb = 0
    datal = (GedcomWriteFam(fen, wri, nb + 1, cursor))
    if datal:
        data.extend(datal)

    """ Write all the objects """
    GedcomWriteObject(fen, wri, cursor)

    """ Write all the sources """
    GedcomWriteSource(fen, wri, data)

    """ Process completed """
    fen.Message(fen.mess["ged05"])
    wri.write("0 TRLR\n")
    wri.close()
    fen.Message(fen.mess["all14"])
    return


def GedcomHeader(fen, wri, gedw):
    """
    Write header file
    input:
        fen     : pointer to window
        wri     : pointer to writing file
        gedw    : name of the file to write
    output:
        nothing
    """
    date = datetime.datetime.now()
    date_s = "%s %s %s" % (date.day, month_gb[date.month - 1],
                           date.year)
    time_s = "%s:%s:%s" % (date.hour, date.minute, date.second)
    fichier = os.path.basename(gedw)

    for ghead in gheader:
        wri.write(ghead)

    wri.write("  1 DATE %s\n" % (date_s))
    wri.write("    2 TIME %s\n" % (time_s))
    wri.write("  1 FILE %s\n" % (fichier))
    wri.write("  1 CHAR UTF-8\n")
    return


def GedcomWriteIndiv(fen, wri, cursor):
    """
    Write individual
    input:
        fen     : pointer to window
        wri     : file to write
        cursor  : pointer to database
    output:
        data    : source list
    """
    param = ('id', 'name', 'firstname', 'sexe')
    rows = SelectTabDb(fen, cursor, 'indiv', param, 'null', 0, 1, 'null')
    i = 1
    data = []
    if rows:
        for row in rows:
            name = []
            firstname = []
            if row[1]:
                name = row[1]
            if row[2]:
                firstname = row[2]
            """ Id of individual """
            wri.write("0 @I%s@ INDI\n" % (row[0]))
            """ Individual name and firstname """
            wri.write("  1 NAME %s /%s/\n" % (firstname, name))
            wri.write("    2 GIVN %s\n" % (firstname))
            wri.write("    2 SURN %s\n" % (name))
            """ Sexe """
            wri.write("  1 SEX %s\n" % (row[3]))

            for eve in event_ind:
                """ Modification du 16 octobre 2021 """
                events = ReadEventSexe(fen, row[0], row[3], eve, cursor)
                if events:
                    for event in events:
                        datal = GedcomWriteEvent(fen, eve, event, wri, i)
                        if datal:
                            data.append(datal)
                            i = 1 + data[-1][0]
            """ Select families """
            if row[3] == 'M':
                fams = SelectTabDb(fen, cursor, 'fam', ('id',), 'idh=?',
                                   (row[0],), 1, 'null')
            else:
                fams = SelectTabDb(fen, cursor, 'fam', ('id',), 'idw=?',
                                   (row[0],), 1, 'null')
            if fams:
                for fam in fams:
                    wri.write("  1 FAMS @F%s@\n" % (fam[0]))
            """ Record object """
            GedcomWriteObjectIndiv(fen, row[0], wri, cursor)
    return data


def GedcomWriteFam(fen, wri, nb, cursor):
    """
    Write family
    input:
        fen     : pointer to window
        wri     : file to write
        nb      : family id
        cursor  : pointer to database
    output:
        data    : source
    """
    data = []
    fams = SelectTabDb(fen, cursor, 'fam', ('*',), 'null', 0, 1, 'null')
    if fams:
        for fam in fams:
            wri.write("0 @F%s@ FAM\n" % (fam[0]))
            if fam[1]:
                wri.write("  1 HUSB @I%s@\n" % (fam[1]))
            if fam[2]:
                wri.write("  1 WIFE @I%s@\n" % (fam[2]))
            """ Search if wedding """
            if fam[1] and fam[2]:
                params = ('day', 'month', 'year', 'city', 'note',
                          'com1', 'source', 'time', 'precision')
                marr = SelectTabDb(fen, cursor, 'event', params,
                                   "(idh=? AND idw=?) AND type='MARR'",
                                   (fam[1], fam[2]), 0, 'null')
                if marr:
                    datal = GedcomWriteEvent(fen, 'MARR', marr, wri, nb)
                    if datal:
                        data.append(datal)
                        nb = 1 + data[-1][0]
                """ Search if children """
                children = SelectTabDb(fen, cursor, 'indiv', ('id',),
                                       'idfather=? AND idmother=?',
                                       (fam[1], fam[2]), 1, 'null')
                if children:
                    for child in children:
                        wri.write("  1 CHIL @I%s@\n" % (child[0]))
            else:
                if fam[1]:
                    children = SelectTabDb(fen, cursor, 'indiv', ('id',),
                                           'idfather=?', (fam[1],), 1,
                                           'null')
                    if children:
                        for child in children:
                            wri.write("  1 CHIL @I%s@\n" % (child[0]))
                if fam[2]:
                    children = SelectTabDb(fen, cursor, 'indiv', ('id',),
                                           'idmother=?', (fam[2],), 1,
                                           'null')
                    if children:
                        for child in children:
                            wri.write("  1 CHIL @I%s@\n" % (child[0]))
    return data


def GedcomWriteObject(fen, wri, cursor):
    """
    Write objects
    input:
        fen     : pointer to window
        wri     : file to write
        cursor  : pointer to database
    output:
        nothing
    """
    params = ('id', 'file', 'form', 'title')
    objects = SelectTabDb(fen, cursor, 'object', params,
                          'null', 0, 1, 'null')
    if objects:
        for object in objects:
            wri.write("0 @M%s@ OBJE\n" % (object[0]))
            if object[1]:
                wri.write("  1 FILE %s\n" % (object[1]))
            else:
                wri.write("  1 FILE\n")
            if object[2]:
                wri.write("    2 FORM %s\n" % (object[2]))
            else:
                wri.write("    2 FORM\n")
            if object[3]:
                wri.write("    2 TITL %s\n" % (object[2]))
            else:
                wri.write("    2 TITL\n")
    return


def GedcomWriteSource(fen, wri, data):
    """
    Write sources
    input:
        fen     : pointer to window
        wri     : file to write
        data    : source data
        cursor  : pointer to database
    output:
        nothing
    """
    for datal in data:
        wri.write("0 @S%s@ SOUR\n" % (datal[0]))
        wri.write("  1 TITL %s\n" % (datal[1]))
    return


def GedcomWriteEvent(fen, eve, event, wri, nb):
    """
    Ecriture d'un évènement
    input:
        fen     : pointer to window
        eve     : type of event
        event   : data event
        wri     : file to write
        nb      : number of source
    output:
        data    : data to save
    """

    data = ""
    wri.write("  1 %s" % (eve))
    """ if com1, additional information """
    if event[5]:
        if eve == 'OCCU':
            wri.write(" %s\n" % (event[5]))
        else:
            if eve == 'RESI':
                wri.write("\n    2 TYPE %s\n" % (event[5]))
            else:
                wri.write("\n")
    else:
        wri.write("\n")

    if event[0] or event[1] or event[2]:
        date = Gedcomdate(fen, event[0], event[1], event[2], event[8])
        wri.write("    2 DATE %s\n" % (date))
        if event[7]:
            wri.write("    2 TIME %s\n" % (event[7]))
    if event[3]:
        wri.write("    2 PLAC %s\n" % (event[3]))
    if event[4]:
        wri.write("    2 NOTE %s\n" % (event[4]))
    if event[6]:
        """ Source """
        wri.write("    2 SOUR @S%s@\n" % (nb))
        data = [nb, event[6]]

    return data


def GedcomWriteObjectIndiv(fen, id, wri, cursor):
    """
    Write an object
    input:
        fen     : pointer to window
        id      : individual id
        wri     : file to write
        cursor  : pointer to database
    output:
        nothing
    """
    params = ('id', 'file', 'form', 'title')
    objects = SelectTabDb(fen, cursor, 'object', params, 'indiv=?',
                          (id,), 1, 'null')
    if objects:
        for object in objects:
            wri.write("  1 OBJE @M%s@\n" % (object[0]))
    return


def Gedcomdate(fen, day, month, year, precision):
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
    if isinstance(month, (int)):
        date = "%s %s" % (date, month_gb[int(month)-1])
    if year:
        date = "%s %s" % (date, year)
    date = date.strip()

    return date
