import json
import os
import shutil
import argparse

from utils import escape_for_tex
from datetime import date, timedelta
from dateutil.parser import parse
from PyPDF2 import PdfReader, PdfMerger


# Parse command line arguments
parser = argparse.ArgumentParser(description='Generate agenda PDF with daily or weekly layout')
parser.add_argument(
    '--mode',
    choices=[
        'day', 'week', 'calendar', 'merge'
    ], default='week',
    help='Layout mode: "day" for 4 days per page (portrait),' +    '"week" for 7 days per page (landscape), ' + 
    '"calendar" for calendar page generation and ' +
    '"merge" to bring it all together'
)
args = parser.parse_args()


eg_dir = '_eg'
calendar_base = 'tmp/calendar'
files_dir = 'tmp'
output_file = 'output.pdf'
pdf_dir = './pdf'

# Cleanup everything before generation.
if args.mode in ['day', 'week']:
    shutil.rmtree(files_dir, ignore_errors=True)
    os.makedirs(files_dir)
    shutil.rmtree(pdf_dir, ignore_errors=True)
    os.makedirs(pdf_dir)

with open('config.json') as config_file:
    config = json.load(config_file)

author = escape_for_tex(config['author'])
first_day = parse(config['first_day'], dayfirst=True).date()
last_day = parse(config['last_day'], dayfirst=True).date()
dates = [first_day + timedelta(days=x) for x in range((last_day-first_day).days + 1)]


if args.mode == 'week':
    # Weekly mode: two portrait pages per week (Mon-Wed, Thu-Sun)
    print(f"Generating agenda in WEEKLY mode (portrait, 2 pages per week)")

    # Group dates by ISO week
    weeks = {}
    for d in dates:
        week_key = d.isocalendar()[:2]  # (year, week_number)
        if week_key not in weeks:
            weeks[week_key] = []
        weeks[week_key].append(d)

    file_name: str = ""
    for week_idx, (week_key, week_dates) in enumerate(sorted(weeks.items())):
        # Ensure we have a full week (pad if necessary)
        # Find Monday of this week
        first_date = min(week_dates)
        monday = first_date - timedelta(days=first_date.weekday())

        # Generate all 7 days for the week
        week_days = [monday + timedelta(days=i) for i in range(7)]

        file_name = os.path.join(files_dir, f'week-{week_key[0]}-{week_key[1]:02d}.txt')
        page_name = os.path.join(pdf_dir, f'week-{week_key[0]}-{week_key[1]:02d}.txt.pdf')

        print(f'Week {week_key[1]} of {week_key[0]}: {week_days[0]} to {week_days[6]}')

        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        with open(file_name, 'wb') as f:
            f.write(bytes('\\def\\thisYear{' + str(dates[0].year) + '}\n', 'UTF-8'))
            f.write(bytes('\\def\\pageName{' + page_name + '}\n', 'UTF-8'))

            for i, (day_name, d) in enumerate(zip(day_names, week_days)):
                datum = d.strftime('%b, %-d')
                day_of_week = d.strftime('%a')
                week = d.isocalendar()[1]

                # Page numbers: Mon-Wed on first page, Thu-Sun on second page
                page_num = week_idx * 2 + (-1 if i < 3 else 0)

                f.write(bytes(f'\\def\\day{day_name}' + '{' + str(d) + '}\n', 'UTF-8'))
                f.write(bytes(f'\\def\\date{day_name}' + '{' + datum + '}\n', 'UTF-8'))
                f.write(bytes(f'\\def\\dayOfWeek{day_name}' + '{' + day_of_week + '}\n', 'UTF-8'))
                f.write(bytes(f'\\def\\week{day_name}' + '{' + str(week) + '}\n', 'UTF-8'))
                f.write(bytes(f'\\def\\page{day_name}' + '{' + str(page_num) + '}\n', 'UTF-8'))

        # Generate PDF for this week (creates 2 pages)
        os.system('pdflatex -interaction=batchmode -jobname=' + file_name + ' agendaPageWeek.tex' + '> /dev/null 2>&1')
        # Copy the generated PDF to the pdf directory with correct path
        os.system('cp ' + file_name + '.pdf pdf/.')


    print(f'Building weekly inlay...')
    os.system('pdflatex -interaction=batchmode -jobname=' + file_name + ' agendaWeek.tex' + '> /dev/null 2>&1')

elif args.mode == 'day':
    # Daily mode: original 4 days per page logic
    print(f"Generating agenda in DAILY mode (portrait, 4 days per page)")

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
                os.system('pdflatex -interaction=batchmode -jobname=' + file_name + ' agendaPage.tex' + '> /dev/null 2>&1')
            os.system('cp ' + page_name + '.pdf pdf/.')
            for k in range(2):
                os.system('pdflatex -interaction=batchmode -jobname=' + file_name + ' agenda.tex' + '> /dev/null 2>&1')
        else:
            i += 1

elif args.mode == 'calendar':
    print(f"Generating agenda calendar (portrait, 4 days per page)")
    # Generate calendar.
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
        os.system('pdflatex -interaction=batchmode -jobname=' + calendar_base + k + '.txt' + ' calendarPage.tex' + '> /dev/null 2>&1')


elif args.mode == 'merge':
    merger = PdfMerger()
    for i in range(3):
        merger.append(
            PdfReader(os.path.join(eg_dir, 'gridded.pdf'), 'rb'))
        merger.append(
            PdfReader(os.path.join(eg_dir, 'dotted.pdf'), 'rb'))

    pdf_files = sorted([f for f in os.listdir(files_dir) if f.endswith('pdf')])
    for f in pdf_files:
        merger.append(PdfReader(os.path.join(files_dir, f), 'rb'))

    for i in range(3):
        merger.append(
            PdfReader(os.path.join(eg_dir, 'gridded.pdf'), 'rb'))
        merger.append(
            PdfReader(os.path.join(eg_dir, 'dotted.pdf'), 'rb'))
    merger.write(output_file)
