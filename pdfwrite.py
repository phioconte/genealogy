""" Generating a pdf file
    Author                        : Ph OCONTE
    Date                          : november 29, 2021
    Date of last update           : november 29, 2021
    Version                       : 1.0.0
"""
import sqlite3
from fpdf import FPDF

from dbmanagment import LinkDb, SelectTabDb
from reference import event_ind, event_gb, event_fam
from display import DisplayDate


class PDF(FPDF):

    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", "I", 8)
        self.set_text_color(0)
        # Printing page number:
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")


def PdfWrite(fen):
    """ Write pdf file
    input:
        fen     : pointer to window
    output:
        nothing
    """
    fen.Message(fen.mess["pdf07"])
    document = PDF()
    document.alias_nb_pages()
    document.add_page()
    PdfHeader(fen, document)
    document.set_font('Times', 'B', 12)
    document.cell(0, 5, fen.mess["pdf00"], 0, 0)
    document.set_font('Times', size=10)
    document.ln()
    document.cell(0, 5, "\n", 0, 0)
    document.ln()

    conn = sqlite3.connect(LinkDb(fen))
    cursor = conn.cursor()

    """ print the list of individuals """
    fen.Message(fen.mess["pdf08"])
    rows = SelectTabDb(fen, cursor, 'indiv', ('*',), 'null', 0, 1,
                       'ORDER BY name, firstname')
    datas = []
    link = []
    if rows:
        for row in rows:
            line = ("%s" % (row[0]), row[1], row[2], row[3])
            datas.append(line)
            # document.cell(txt=line, ln=ln)
        headings = (fen.mess["lab29"], fen.mess["lab30"], fen.mess["lab31"])
        col_widths = (10, 30, 50)
        aligns = ('R', 'RF', 'RF')
        link = PdfTableList(fen, document, headings, datas, col_widths,
                            aligns, 10, 10)

    """ Print the datas of each individual """
    fen.Message(fen.mess["pdf09"])
    PdfWriteEachIndiv(fen, cursor, document, link)

    """ Print the datas of each city """
    fen.Message(fen.mess["pdf10"])
    document.add_page(orientation='L', format='A4', same=False)
    PdfWriteCities(fen, cursor, document)

    """ file to write """
    file = "%s/%s" % (fen.WorkingDirectory, fen.PdfFile)
    document.output(file)

    fen.Message(fen.mess["pdf11"])
    return


def PdfWriteEachIndiv(fen, cursor, doc, links):
    """
    write data for each individual
    input:
        fen     : pointer to window
        cursor  : pointer to database
        doc     : write file
        links   : link to each individual
    output:
        nothing
    """
    page_indiv = []
    numero_page = 1 + doc.page_no()
    rows = SelectTabDb(fen, cursor, 'indiv', ('*',), 'null', 0, 1,
                       'ORDER BY name, firstname')
    if rows:
        for row in rows:
            line = (row[0], numero_page)
            page_indiv.append(line)
            numero_page += 1

    rows = SelectTabDb(fen, cursor, 'indiv', ('*',), 'null', 0, 1,
                       'ORDER BY name, firstname')
    i = 0
    if rows:
        for row in rows:
            doc.add_page()
            PdfHeader(fen, doc)
            doc.set_link(links[i], y = 0, page = -1)
            i = i + 1
            """ Select the photo if it exists """
            fimages = SelectTabDb(fen, cursor, 'object', ('file', 'form'),
                                  'indiv=?', (row[0],), 1, 'null')
            if fimages:
                for fimage in fimages:
                    if fimage[0] and fimage[1]:
                        if fimage[1] == 'jpg':
                            image = "%s" % (fimage[0])
                            doc.image(image, 10, 8, 33)
                            doc.ln()
                            doc.cell(0, 5, "\n", 0, 0)
                            doc.ln()
            headings = (fen.mess["lab29"], fen.mess["lab30"],
                        fen.mess["lab31"], fen.mess["lab32"])
            col_widths = (15, 45, 80, 18)
            aligns = ('RF', 'RF', 'RF', 'C')
            datas = []
            line = ("%s" % (row[0]), row[1], row[2], row[3])
            datas.append(line)
            PdfTable(fen, doc, headings, datas, col_widths, aligns, 12, 12)
            doc.ln()
            doc.cell(0, 5, "\n", 0, 0)
            doc.ln()
            PdfWriteCivil(fen, row[0], doc, row[3], cursor)
            PdfWriteFamily(fen, row[0], doc, row[3], cursor, page_indiv)

    return


def PdfWriteCivil(fen, id, doc, sexe, cursor):
    """
    Definition of the civil status of the individual
    input:
        fen     : pointer to window
        id      : individual id
        doc     : file to write
        sexe    : sexe of individual
        cursor  : pointer to database
    output:
        nothing
    """

    """ Write all deeds for individual """
    datas = []
    for eventx in event_ind:
        data = (PdfWriteEvent(fen, id, eventx, doc, cursor, 0, 0))
        if data is not None:
            datas.append(data)
    if datas:
        doc.set_font("Times", "B", 14)
        doc.cell(0, 5, fen.mess["pdf02"], 0, 0)
        doc.ln()
        doc.cell(0, 5, "\n", 0, 0)
        doc.ln()
        headings = (fen.mess["col00"], fen.mess["col01"], fen.mess["col02"],
                    fen.mess["col03"], fen.mess["col04"], fen.mess["col06"])
        col_widths = (15, 23, 55, 28, 43, 28)
        aligns = ('RF', 'RF', 'RF', 'RF', 'RF', 'RF')
        PdfTable(fen, doc, headings, datas, col_widths, aligns, 10, 8)
        doc.ln()
    return


def PdfWriteEvent(fen, id, eventx, doc, cursor, flag, ids):
    """
    write event
    input:
        fen     : pointer to window
        id      : individual id
        eventx  : event to select
        doc     : write file
        cursor  : pointer to database
        flag    : 0 = event to indidual, 1 = event to family
        ids     : Spouse id
    output:
        line    : datas of event or None if not event
    """
    param = ('day', 'month', 'year', 'precision', 'city',
             'note', 'source', 'com1')
    if flag == 0:           # Event individual
        event = SelectTabDb(fen, cursor, 'event', param,
                            '(idh=? OR idw=?) AND type=?',
                            (id, id, eventx), 0, 'null')
    else:
        event = SelectTabDb(fen, cursor, 'event', param,
                            'idh=? AND idw=? AND type=?',
                            (id, ids, eventx), 0, 'null')
    line = ["", "", "", "", "", ""]
    if event:
        line[0] = fen.LocEvent[event_gb.index(eventx) - 1]
        if eventx == 'OCCU' or eventx == 'RESI':
            line[5] = PdfWriteAnalysLine(fen, event[7])
            # line[5] = event[7].encode('latin-1', 'replace').decode('latin-1')
        date = DisplayDate(fen, event[0], event[1], event[2], event[3])
        if date is not None and len(date) > 0:
            line[1] = PdfWriteAnalysLine(fen, date)
            # line[1] = date.encode('latin-1', 'replace').decode('latin-1')
        if event[4]:                # City
            city = event[4].split(',')
            cit = "%s %s (%s)" % (city[3], city[1], city[6])
            cit = cit.strip()
            line[2] = PdfWriteAnalysLine(fen, cit)
            # line[2] = cit.encode('latin-1', 'replace').decode('latin-1')
        if event[5]:
            line[3] = PdfWriteAnalysLine(fen, event[5])
            # line[3] = event[5].encode('latin-1', 'replace').decode('latin-1')
        if event[6]:
            line[4] = PdfWriteAnalysLine(fen, event[6])
            # line[4] = event[6].encode('latin-1', 'replace').decode('latin-1')
        return line
    return None


def PdfWriteFamily(fen, id, doc, sexe, cursor, page_indiv):
    """
    Define the family
    input:
        fen        : pointer to window
        id         : individual id
        doc        : file to write
        sexe       : individual sexe
        cursor     : pointer to database
        page_indiv : individual id and link to individual
    output:
        nothing
    """
    doc.ln()
    doc.cell(0, 5, "\n", 0, 0)
    doc.ln()
    doc.set_font("Times", "BU", 14)
    doc.cell(0, 5, fen.mess["pdf03"], 0, 0)
    doc.set_font("Times", size=12)
    doc.ln()
    """ Search father and mother """
    parent = SelectTabDb(fen, cursor, 'indiv', ('idfather', 'idmother'),
                         'id=?', (id,), 0, 'null')
    doc.set_font("Courier", size=10)
    if parent:
        if parent[0] is not None:
            father = SelectTabDb(fen, cursor, 'indiv', ('name', 'firstname'),
                                 'id=?', (parent[0],), 0, 'null')
            if father:
                PdfIndivLink(fen, doc, parent[0], father[0], father[1],
                             fen.mess["lab05"], page_indiv)
        if parent[1] is not None:
            mother = SelectTabDb(fen, cursor, 'indiv', ('name', 'firstname'),
                                 'id=?', (parent[1],), 0, 'null')
            if mother:
                PdfIndivLink(fen, doc, parent[1], mother[0], mother[1],
                             fen.mess["lab06"], page_indiv)
    """ Search spouses """
    if sexe == 'M':
        fams = SelectTabDb(fen, cursor, 'fam', ('idw',), 'idh=?',
                           (id,), 1, 'null')
    else:
        fams = SelectTabDb(fen, cursor, 'fam', ('idh',), 'idw=?',
                           (id,), 1, 'null')
    if fams:
        doc.cell(0, 5, "\n", 0, 0)
        doc.ln()
        doc.set_font("Times", "B", 12)
        doc.cell(0, 5, fen.mess["pdf04"], 0, 0)
        doc.ln()
        doc.cell(0, 5, "\n", 0, 0)
        doc.ln()
        for fam in fams:
            if fam[0]:
                spouse = SelectTabDb(fen, cursor, 'indiv',
                                     ('name', 'firstname'),
                                     'id=?', (fam[0],), 0, 'null')
                PdfIndivLink(fen, doc, fam[0], spouse[0], spouse[1],
                             "", page_indiv)
                datas = []
                for eventx in event_fam:
                    if sexe == 'M':
                        data = PdfWriteEvent(fen, id, eventx, doc, cursor,
                                             1, fam[0])
                    else:
                        data = PdfWriteEvent(fen, fam[0], eventx, doc, cursor,
                                             1, id)
                    if data is not None:
                        datas.append(data)
                if datas:
                    headings = (fen.mess["col00"], fen.mess["col01"],
                                fen.mess["col02"], fen.mess["col03"],
                                fen.mess["col04"], fen.mess["col06"])
                    col_widths = (15, 23, 55, 28, 43, 28)
                    aligns = ('RF', 'RF', 'RF', 'RF', 'RF', 'RF')
                    PdfTable(fen, doc, headings, datas, col_widths,
                             aligns, 10, 8)
                    doc.ln()

    """ Search children """
    if sexe == 'F':
        children = SelectTabDb(fen, cursor, 'indiv',
                               ('id', 'name', 'firstname'),
                               'idmother=?', (id,), 1,
                               'ORDER BY name, firstname')
    else:
        children = SelectTabDb(fen, cursor, 'indiv',
                               ('id', 'name', 'firstname'),
                               'idfather=?', (id,), 1,
                               'ORDER BY name, firstname')
    if children:
        doc.cell(0, 5, "\n", 0, 0)
        doc.ln()
        doc.set_font("Times", "B", 12)
        doc.cell(0, 5, fen.mess["pdf05"], 0, 0)
        doc.ln()
        doc.cell(0, 5, "\n", 0, 0)
        doc.ln()
        doc.set_font("Courier", size=10)
        for child in children:
            PdfIndivLink(fen, doc, child[0], child[1], child[2],
                         "", page_indiv)

    """ Search brother(s) and sister(s) """
    PdfWriteBrSi(fen, id, doc, cursor, page_indiv)
    return


def PdfTableList(fen, doc, headings, rows, col_widths, aligns,
                 headersize, linesize):
    """ Write the individuals list
    input:
        fen        : pointer to window
        doc        : file to write
        headings   : header of the table
        rows       : datas to write (id, name and firstname)
        col_widths : width of each column
        aligns     : align od each column
        headersize : size of the header line
        linesize   : size of the current lines
    output:
        links      : link to each indiviudal
    """
    PdfWriteHeaderTable(fen, doc, col_widths, headings, headersize,
                        linesize)
    line_height = doc.font_size * 1.2
    fill = False
    links = []
    nb_lib = 33
    for row in rows:
        if doc.will_page_break(line_height):
            PdfHeader(fen, doc)
            PdfWriteHeaderTable(fen, doc, col_widths, headings, headersize,
                                linesize)
            nb_lig = 40
        doc.cell(col_widths[0], 6, row[0], 1, 0, aligns[0], fill)
        doc.set_font(style="U")
        link = doc.add_link()
        links.append(link)
        doc.cell(col_widths[1], 6, row[1], 1, 0, aligns[1], fill, link)
        doc.set_font()
        doc.cell(col_widths[2], 6, row[2], 1, 0, aligns[2], fill)
        doc.ln()
        fill = not fill
    # Closure line:
    doc.cell(sum(col_widths), 0, "", "T")
    return links


def PdfTable(fen, doc, headings, rows, col_widths, aligns,
             headersize, linesize):
    """ Write table
    input:
        fen        : pointer to window
        doc        : file to write
        headings   : header of the table
        rows       : datas to write (id, name and firstname)
        col_widths : width of each column
        aligns     : align od each column
        headersize : size of the header line
        linesize   : size of the current lines
    output:
        nothing
    """
    PdfWriteHeaderTable(fen, doc, col_widths, headings, headersize,
                        linesize)
    line_height = doc.font_size * 1.5
    fill = False
    for row in rows:
        if doc.will_page_break(line_height):
            PdfHeader(fen, doc)
            PdfWriteHeaderTable(fen, doc, col_widths, headings, headersize,
                                linesize)
        for i in range(0, len(col_widths)):
            doc.cell(col_widths[i], 6, row[i], 1, 0, aligns[i], fill)
        doc.ln()
        fill = not fill
    # Closure line:
    doc.cell(sum(col_widths), 0, "", "T")
    return


def PdfWriteBrSi(fen, id, doc, cursor, page_indiv):
    """
    Search brothers and sisters
    input:
        fen        : pointer to window
        id         : individual id
        doc        : file to write
        sexe       : individual sexe
        cursor     : pointer to database
        page_indiv : link to card of individual
    output:
        nothing
    """
    doc.cell(0, 5, "\n", 0, 0)
    doc.ln()
    row = SelectTabDb(fen, cursor, 'indiv', ('idfather', 'idmother'),
                      'id=?', (id,), 0, 'null')
    if row[0] and row[1]:
        brsi = SelectTabDb(fen, cursor, 'indiv',
                           ('id', 'name', 'firstname'),
                           'idfather=? AND idmother=? AND NOT id=?',
                           (row[0], row[1], id), 1, 'null')
        if brsi:
            doc.set_font('Times', 'B', 12)
            doc.cell(0, 5, fen.mess["pdf06"], 0, 0)
            doc.ln()
            doc.cell(0, 5, "\n", 0, 0)
            doc.ln()
            doc.set_font('Courier', size=10)
            for brs in brsi:
                PdfIndivLink(fen, doc, brs[0], brs[1], brs[2],
                             "", page_indiv)
    else:
        if row[0]:
            brsi = SelectTabDb(fen, cursor, 'indiv',
                               ('id', 'name', 'firstname'),
                               'idfather=? AND NOT id=?',
                               (row[0], id), 1, 'null')
            if brsi:
                doc.set_font('Times', 'B', 12)
                doc.cell(0, 5, fen.mess["pdf06"], 0, 0)
                doc.ln()
                doc.cell(0, 5, "\n", 0, 0)
                doc.ln()
                doc.set_font('Courier', size=10)
                for brs in brsi:
                    PdfIndivLink(fen, doc, brs[0], brs[1], brs[2],
                                 "", page_indiv)
        else:
            if row[1]:
                brsi = SelectTabDb(fen, cursor, 'indiv',
                                   ('id', 'name', 'firstname'),
                                   'idmother=? AND NOT id=?',
                                   (row[1], id), 1, 'null')
                if brsi:
                    doc.set_font('Times', 'B', 12)
                    doc.cell(0, 5, fen.mess["pdf06"], 0, 0)
                    doc.ln()
                    doc.cell(0, 5, "\n", 0, 0)
                    doc.ln()
                    doc.set_font('Courier', size=10)
                    for brs in brsi:
                        PdfIndivLink(fen, doc, brs[0], brs[1], brs[2],
                                     "", page_indiv)
    return


def PdfWriteHeaderTable(fen, doc, col_widths, headings, headersize, linesize):
    """ Write the header of table
    input:
        fen        : pointer to window
        doc        : file to write
        col_widths : width of each column
        headings   : header of the table
        headersize : size of the header line
        linesize   : size of the current lines
    output:
        nothing
    """
    doc.set_fill_color(255, 100, 0)
    doc.set_text_color(255)
    doc.set_draw_color(255, 0, 0)
    doc.set_line_width(0.3)
    doc.set_font('Times', 'B', headersize)
    for col_width, heading in zip(col_widths, headings):
        doc.cell(col_width, 7, heading, 1, 0, "C", True)
    doc.ln()
    doc.set_fill_color(224, 235, 255)
    doc.set_text_color(0)
    doc.set_font('Times', size=linesize)
    return


def PdfWriteCities(fen, cursor, doc):
    """ Write all cities
    input:
        fen     : pointer to window
        cursor  : pointer to database
        doc     : file to write
    output:
        nothing
    """
    params = ('locality', 'city', 'Insee', 'Postal', 'dep', 'district',
              'country')
    cities = SelectTabDb(fen, cursor, 'city', params, 'null', 0,
                         1, 'null')
    datas = []
    if cities:
        for city in cities:
            line = [None, None, None, None, None, None, None]
            for i in range(0, 7):
                # line[i] = city[i].encode('latin-1', 'replace').decode('latin-1')
                line[i] = PdfWriteAnalysLine(fen, city[i])
                if i == 2 or i == 3:
                    if line[i]:
                        line[i] = "%05d" % (int(line[i]))
            datas.append(line)
    if datas:
        PdfHeader(fen, doc)
        headings = (fen.mess["col10"], fen.mess["col11"], fen.mess["pdf12"],
                    fen.mess["pdf13"], fen.mess["col14"], fen.mess["col15"],
                    fen.mess["col16"])
        col_widths = (33, 54, 15, 15, 60, 62, 30)
        aligns = ('RF', 'RF', 'C', 'C', 'RF', 'RF', 'RF')
        PdfTable(fen, doc, headings, datas, col_widths, aligns,
                 12, 10)
    return


def PdfHeader(fen, doc):
    """ Write the header of each page
    input:
        fen     : pointer to window
        doc     : file to write
    output:
        nothing
    """
    doc.set_fill_color(255, 100, 0)
    doc.set_text_color(0)
    doc.set_draw_color(255, 0, 0)
    # Setting font: helvetica bold 15
    doc.set_font("helvetica", "B", 14)
    # Moving cursor to the right:
    doc.cell(80)
    # Printing title:
    doc.cell(60, 10, fen.mess["pdf01"], 1, 0, "C")
    # Performing a line break:
    doc.ln(20)
    return


def PdfIndivLink(fen, doc, id, name, firstname, title, page_indiv):
    """ Write the link to individual card
    input:
        fen        : pointer to window
        doc        : file to write
        id         : individual id
        name       : name
        firstname  : firstname
        title      : title of the line
        page_indiv : Table of id and link
    output:
        nothing
    """
    if len(title) > 0:
        line = "%s : (%-4d) %s %s" % (title, int(id), name, firstname)
    else:
        line = "(%-4d) %s %s" % (int(id), name, firstname)
    page = PdfSelectPage(fen, id, page_indiv)
    link = doc.add_link()
    doc.set_link(link, page=page)
    doc.set_font("Courier", "U", 10)
    doc.cell(0, 5, line, 0, 0, link=link)
    doc.set_font("Courier", size=10)
    doc.ln()
    return


def PdfSelectPage(fen, id, page_indiv):
    """ Select the page of the individual
    input:
        fen        : pointer to window
        id         : individual id
        page_indiv : id and link
    output:
        nothing
    """
    page = 1

    for i in range(0, len(page_indiv)):
        if id == page_indiv[i][0]:
            return(page_indiv[i][1])
    return page


def PdfWriteAnalysLine(fen, line):
    """ Analyse the letters of the line
    input:
        fen     : pointer to window
        line    : line to analyse
    output:
        data    : line after analyse
    """
    data = []
    for i in range(0, len(line)):
        if line[i] == "\u2019":
            data.append("'")
        else:
            data.append(line[i])
    outputline = ''.join(data)
    return outputline
