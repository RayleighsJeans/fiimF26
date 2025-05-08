import json
import os
import shlex
import shutil
import subprocess

from utils import escape_for_tex
from datetime import date, timedelta
from dateutil.parser import parse
from PyPDF2 import PdfReader, PdfMerger

eg_dir = '_eg'

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
for d in dates:
    if i == 0:
        file_name = os.path.join(files_dir, str(d) + '.txt')
        page_name = os.path.join(files_dir, str(d) + '.txt')
        agenda_page = os.path.join(pdf_dir, str(d) + '.txt.pdf')

    date = d.strftime('%b, %-d')
    day_of_week = d.strftime('%a')

    if True:
        print('(' + str(i) + ')', end=' ')
        print(d, end=' ')
        print(date, end=' ')
        print(day_of_week, end=' ')
        print(file_name, end=' ')
        print(page_name, end=' ')
        print(agenda_page)

    if i == 0:
        fields = ['dayA', 'dateA', 'dayOfWeekA']
    elif i == 1:
        fields = ['dayB', 'dateB', 'dayOfWeekB']
    elif i == 2:
        fields = ['dayC', 'dateC', 'dayOfWeekC']
    else:
        fields = ['dayD', 'dateD', 'dayOfWeekD']

    with open(file_name, 'ab') as f:
        if i == 0:
            f.write(bytes('\\def\\pageName{' + agenda_page + '}\n', 'UTF-8'))
        f.write(bytes('\\def\\' + fields[0] + '{' + str(d) + '}\n', 'UTF-8'))
        f.write(bytes('\\def\\' + fields[1] + '{' + date + '}\n', 'UTF-8'))
        f.write(bytes('\\def\\' + fields[2] + '{' + day_of_week + '}\n', 'UTF-8'))

    if i == 3:
        i = 0
        for k in range(2):
            os.system('pdflatex -interaction=batchmode -jobname=' + file_name + ' agendaPage.tex')
        os.system('cp ' + page_name + '.pdf pdf/.')
        for k in range(2):
            os.system('pdflatex -interaction=batchmode -jobname=' + file_name + ' agenda.tex')
    else:
        i += 1

merger = PdfMerger()
for i in range(5):
    merger.append(
        PdfReader(os.path.join(eg_dir, 'gridded.pdf'), 'rb'))
    merger.append(
        PdfReader(os.path.join(eg_dir, 'dotted.pdf'), 'rb'))
pdf_files = sorted([f for f in os.listdir(files_dir) if f.endswith('pdf')])
for f in pdf_files:
    merger.append(PdfReader(os.path.join(files_dir, f), 'rb'))
for i in range(5):
    merger.append(
        PdfReader(os.path.join(eg_dir, 'gridded.pdf'), 'rb'))
    merger.append(
        PdfReader(os.path.join(eg_dir, 'dotted.pdf'), 'rb'))
merger.write(output_file)
