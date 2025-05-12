import json
import os
import shutil

from utils import escape_for_tex
from datetime import date, timedelta
from dateutil.parser import parse
from PyPDF2 import PdfReader, PdfMerger

eg_dir = '_eg'

calendar_base = 'tmp/calendar'
files_dir = 'tmp'
output_file = 'output.pdf'
shutil.rmtree(files_dir, ignore_errors=True)
os.makedirs(files_dir)

pdf_dir = './pdf'
shutil.rmtree(pdf_dir, ignore_errors=True)
os.makedirs(pdf_dir)

with open('config.json') as config_file:
    config = json.load(config_file)

author = escape_for_tex(config['author'])
first_day = parse(config['first_day'], dayfirst=True).date()
last_day = parse(config['last_day'], dayfirst=True).date()
dates = [first_day + timedelta(days=x) for x in range((last_day-first_day).days + 1)]

i = 0
for j, d in enumerate(dates):
    if i == 0:
        file_name = os.path.join(files_dir, str(d) + '.txt')
        page_name = os.path.join(files_dir, str(d) + '.txt')
        agenda_page = os.path.join(pdf_dir, str(d) + '.txt.pdf')

    datum = d.strftime('%b, %-d')
    month = d.strftime('%b')
    day_of_week = d.strftime('%a')
    week = date(d.year, d.month, d.day).isocalendar()[1]

    if True:
        print('(' + str(i) + ', ' + str(j) + ')', end=' ')
        print(d, end=' ')
        print(datum, end=' ')
        print(day_of_week + '(' + str(week) + ')', end=' ')
        print(file_name, end=' ')
        print(page_name, end=' ')
        print(agenda_page)

    if i == 0:
        fields = ['dayA', 'dateA', 'dayOfWeekA', 'weekA', 'pageA']
    elif i == 1:
        fields = ['dayB', 'dateB', 'dayOfWeekB', 'weekB', 'pageB']
    elif i == 2:
        fields = ['dayC', 'dateC', 'dayOfWeekC', 'weekC', 'pageC']
    else:
        fields = ['dayD', 'dateD', 'dayOfWeekD', 'weekD', 'pageD']

    with open(file_name, 'ab') as f:
        if i == 0:
            f.write(bytes('\\def\\pageName{' + agenda_page + '}\n', 'UTF-8'))
        f.write(bytes('\\def\\' + fields[0] + '{' + str(d) + '}\n', 'UTF-8'))
        f.write(bytes('\\def\\' + fields[1] + '{' + datum + '}\n', 'UTF-8'))
        f.write(bytes('\\def\\' + fields[2] + '{' + day_of_week + '}\n', 'UTF-8'))
        f.write(bytes('\\def\\' + fields[3] + '{' + str(week) + '}\n', 'UTF-8'))
        f.write(bytes('\\def\\' + fields[4] + '{' + str(j) + '}\n', 'UTF-8'))

    if i == 3:
        i = 0
        for k in range(2):
            os.system('pdflatex -interaction=batchmode -jobname=' + file_name + ' agendaPage.tex')
        os.system('cp ' + page_name + '.pdf pdf/.')
        for k in range(2):
            os.system('pdflatex -interaction=batchmode -jobname=' + file_name + ' agenda.tex')
    else:
        i += 1


calendar_first = parse(config['calendar_first'], dayfirst=True).date()
calendar_last = parse(config['calendar_last'], dayfirst=True).date()
calendar_dates = [first_day + timedelta(days=x) for x in range((calendar_last-calendar_first).days + 1)]
month_sets = {
    'Jan':1,  'Feb':1, 'Mar':1.5, 'Apr':1.5, 'May':3, 'Jun':3, 'Jul':3.5 , 'Aug':3.5,
    'Sep':5, 'Oct':5, 'Nov':5.5, 'Dec':5.5
}

i = 0
weekList = ''
thisYear = dates[0].year
for j, d in enumerate(calendar_dates):
    datum = d.strftime('%b, %-d')
    month = d.strftime('%b')
    day_of_week = d.strftime('%a')
    week = date(d.year, d.month, d.day).isocalendar()[1]
        
    if j == 0:
        thisWeek = week
        thisMonthSet = month_sets[month]
        firstDate = d
        previousDay = d
        weekList += f'{d.month:02}' + '/' + f'{d.day:02}' + '/' + str(thisWeek)

    if thisWeek != week:
        thisWeek = week
        if month_sets[month] == thisMonthSet:
            weekList += ',' + f'{d.month:02}' + '/' + f'{d.day:02}' + '/' + str(thisWeek)

    if month_sets[month] != thisMonthSet:
        lastDate = previousDay
        with open(calendar_base + str(i) + str(int(thisMonthSet)) + '.txt', 'ab') as f:
            if month_sets[month] - thisMonthSet < 1 and month != 'Jan':
                if month == 'Nov':
                    f.write(bytes('\\def\\year{' + str(d.year) + '}\n', 'UTF-8'))
                f.write(bytes('\\def\\lastDateL{' + str(lastDate) + '}\n', 'UTF-8'))
                f.write(bytes('\\def\\firstDateL{' + str(firstDate) + '}\n', 'UTF-8'))
                f.write(bytes('\\def\\weekSetL{' + weekList + '}\n', 'UTF-8'))
            else:
                if month != 'Jan':
                    f.write(bytes('\\def\\year{' + str(d.year) + '}\n', 'UTF-8'))
                f.write(bytes('\\def\\firstDateR{' + str(firstDate) + '}\n', 'UTF-8'))
                f.write(bytes('\\def\\lastDateR{' + str(lastDate) + '}\n', 'UTF-8'))
                f.write(bytes('\\def\\weekSetR{' + weekList + '}\n', 'UTF-8'))

            if d.year != thisYear:
                i += 1
                thisYear = d.year
        thisMonthSet = month_sets[month]
        weekList = f'{d.month:02}' + '/' + f'{d.day:02}' + '/' + str(thisWeek)
        firstDate = d
    previousDay = d

for k in ['01', '03', '05', '11', '13', '15']:
    os.system('pdflatex -interaction=batchmode -jobname=' + calendar_base + k + '.txt' + ' calendarPage.tex')

merger = PdfMerger()
for i in range(5):
    merger.append(
        PdfReader(os.path.join(eg_dir, 'gridded.pdf'), 'rb'))
    merger.append(
        PdfReader(os.path.join(eg_dir, 'dotted.pdf'), 'rb'))

pdf_files = sorted([f for f in os.listdir(files_dir) if f.endswith('pdf')])
for f in pdf_files[::-1]:
    merger.append(PdfReader(os.path.join(files_dir, f), 'rb'))

for i in range(5):
    merger.append(
        PdfReader(os.path.join(eg_dir, 'gridded.pdf'), 'rb'))
    merger.append(
        PdfReader(os.path.join(eg_dir, 'dotted.pdf'), 'rb'))
merger.write(output_file)
