"""
Module for generating agenda PDFs with daily, weekly, or calendar layouts.
"""
import json
import os
import shutil
import argparse
from datetime import date, timedelta

from dateutil.parser import parse
from PyPDF2 import PdfReader, PdfMerger

from utils import escape_for_tex


# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Generate agenda PDF with daily or weekly layout'
)
parser.add_argument(
    '--mode',
    choices=[
        'day', 'week', 'calendar', 'merge'
    ], default='week',
    help='Layout mode: "day" for 4 days per page (portrait), '
    '"week" for 7 days per page (landscape), '
    '"calendar" for calendar page generation and '
    '"merge" to bring it all together'
)
args = parser.parse_args()


OUTPUT_FILE = 'final/output.pdf'
CALENDAR_BASE = 'tmp/calendar'

EG_DIR = './_eg'
FILES_DIR = './tmp'
PDF_DIR = './pdf'
FINAL_DIR = './final'


def cleanup(mode: str = 'day') -> None:
    """
    Clean up and create necessary directories before generation.
    
    Args:
        mode: The generation mode ('day', 'week', 'calendar', or 'merge')
    """
    if mode in ['day', 'week', 'calendar']:
        if os.path.exists(FILES_DIR):
            shutil.rmtree(FILES_DIR, ignore_errors=True)
        if os.path.exists(PDF_DIR):
            shutil.rmtree(PDF_DIR, ignore_errors=True)

    if not os.path.exists(FILES_DIR):
        os.makedirs(FILES_DIR)
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)
    if not os.path.exists(FINAL_DIR):
        os.makedirs(FINAL_DIR)


cleanup(mode=args.mode)
with open('config.json', encoding='utf-8') as config_file:
    config = json.load(config_file)

AUTHOR = escape_for_tex(config['author'])
FIRST_DAY = parse(config['first_day'], dayfirst=True).date()
LAST_DAY = parse(config['last_day'], dayfirst=True).date()
dates = [
    FIRST_DAY + timedelta(days=x)
    for x in range((LAST_DAY - FIRST_DAY).days + 1)
]


if args.mode == 'week':
    # Weekly mode: two portrait pages per week (Mon-Wed, Thu-Sun)
    print("Generating agenda in WEEKLY mode (portrait, 2 pages per week)")

    # Group dates by ISO week
    weeks = {}
    for d in dates:
        week_key = d.isocalendar()[:2]  # (year, week_number)
        if week_key not in weeks:
            weeks[week_key] = []
        weeks[week_key].append(d)

    file_name = ""
    for week_idx, (week_key, week_dates) in enumerate(sorted(weeks.items())):
        # Ensure we have a full week (pad if necessary)
        # Find Monday of this week
        first_date = min(week_dates)
        monday = first_date - timedelta(days=first_date.weekday())

        # Generate all 7 days for the week
        week_days = [monday + timedelta(days=i) for i in range(7)]

        file_name = os.path.join(
            FILES_DIR, f'week-{week_key[0]}-{week_key[1]:02d}.txt'
        )
        page_name = os.path.join(
            PDF_DIR, f'week-{week_key[0]}-{week_key[1]:02d}.txt.pdf'
        )

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
        os.system(
            f'pdflatex -interaction=batchmode -jobname={file_name} '
            'agendaPageWeek.tex > /dev/null 2>&1'
        )
        # Copy the generated PDF to the pdf directory with correct path
        os.system(f'cp {file_name}.pdf pdf/.')

    print('Building weekly inlay...')
    for k in range(2):
        os.system(
            f'pdflatex -interaction=batchmode -jobname={file_name} '
            'agendaWeek.tex > /dev/null 2>&1'
        )
    os.system(f'cp {file_name}.pdf final/.')


elif args.mode == 'day':
    # Daily mode: original 4 days per page logic
    print("Generating agenda in DAILY mode (portrait, 4 days per page)")

    i = 0
    file_name = ''
    page_name = ''
    agenda_page = ''
    for j, d in enumerate(dates):
        if i == 0:
            file_name = os.path.join(FILES_DIR, str(d) + '.txt')
            page_name = os.path.join(FILES_DIR, str(d) + '.txt')
            agenda_page = os.path.join(PDF_DIR, str(d) + '.txt.pdf')

        datum = d.strftime('%b, %-d')
        month = d.strftime('%b')
        day_of_week = d.strftime('%a')
        week = date(d.year, d.month, d.day).isocalendar()[1]

        # Debug output
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
                os.system(
                    f'pdflatex -interaction=batchmode -jobname={file_name} '
                    'agendaPage.tex > /dev/null 2>&1'
                )
            os.system(f'cp {page_name}.pdf pdf/.')
            for k in range(2):
                os.system(
                    f'pdflatex -interaction=batchmode -jobname={file_name} '
                    'agenda.tex > /dev/null 2>&1'
                )
            os.system(f'cp {file_name}.pdf final/.')
        else:
            i += 1

elif args.mode == 'calendar':
    print("Generating agenda calendar (landscape, 4 months per page)")

    # Generate calendar.
    calendar_first = parse(config['calendar_first'], dayfirst=True).date()
    calendar_last = parse(config['calendar_last'], dayfirst=True).date()
    calendar_dates = [
        FIRST_DAY + timedelta(days=x)
        for x in range((calendar_last - calendar_first).days + 1)
    ]
    month_sets = {
        'Jan':1,  'Feb':1, 'Mar':1.5, 'Apr':1.5, 'May':3, 'Jun':3, 'Jul':3.5 , 'Aug':3.5,
        'Sep':5, 'Oct':5, 'Nov':5.5, 'Dec':5.5
    }

    i = 0
    week_list = ''
    this_year = dates[0].year
    this_month_set = None  # Initialize to avoid possibly-used-before-assignment
    this_week = 0
    first_date = None
    previous_day = None

    for j, d in enumerate(calendar_dates):
        datum = d.strftime('%b, %-d')
        month = d.strftime('%b')
        day_of_week = d.strftime('%a')
        week = date(d.year, d.month, d.day).isocalendar()[1]

        if j == 0:
            this_week = week
            this_month_set = month_sets[month]
            first_date = d
            previous_day = d
            week_list += f'{d.month:02}/{d.day:02}/{this_week}'

        if this_week != week:
            this_week = week
            if month_sets[month] == this_month_set:
                week_list += f',{d.month:02}/{d.day:02}/{this_week}'

        if this_month_set is not None and month_sets[month] != this_month_set:
            last_date = previous_day
            cal_file = f'{CALENDAR_BASE}{i}{int(this_month_set)}.txt'
            with open(cal_file, 'ab') as f:
                if month_sets[month] - this_month_set < 1 and month != 'Jan':
                    if month == 'Nov':
                        f.write(
                            bytes(f'\\def\\thisYear{{{d.year}}}\n', 'UTF-8')
                        )
                    f.write(bytes(f'\\def\\lastDateL{{{last_date}}}\n', 'UTF-8'))
                    f.write(bytes(f'\\def\\firstDateL{{{first_date}}}\n', 'UTF-8'))
                    f.write(bytes(f'\\def\\weekSetL{{{week_list}}}\n', 'UTF-8'))
                else:
                    if month != 'Jan':
                        f.write(
                            bytes(f'\\def\\thisYear{{{d.year}}}\n', 'UTF-8')
                        )
                    f.write(bytes(f'\\def\\firstDateR{{{first_date}}}\n', 'UTF-8'))
                    f.write(bytes(f'\\def\\lastDateR{{{last_date}}}\n', 'UTF-8'))
                    f.write(bytes(f'\\def\\weekSetR{{{week_list}}}\n', 'UTF-8'))

                if d.year != this_year:
                    i += 1
                    this_year = d.year
            this_month_set = month_sets[month]
            week_list = f'{d.month:02}/{d.day:02}/{this_week}'
            first_date = d
        previous_day = d

    for k in ['01', '03', '05', '11', '13', '15']:
        os.system(
            f'pdflatex -interaction=batchmode -jobname={CALENDAR_BASE}{k}.txt '
            'calendarPage.tex > /dev/null 2>&1'
        )
        os.system(f'cp {CALENDAR_BASE}{k}.txt.pdf pdf/.')

    print('Building calendar inlay...')
    os.system(
        f'pdflatex -interaction=batchmode -jobname={CALENDAR_BASE}01.txt '
        'agendaCalendar.tex > /dev/null 2>&1'
    )
    os.system(f'cp {CALENDAR_BASE}01.txt.pdf final/.')


elif args.mode == 'merge':
    merger = PdfMerger()
    for i in range(3):
        merger.append(
            PdfReader(os.path.join(EG_DIR, 'gridded.pdf'), 'rb'))
        merger.append(
            PdfReader(os.path.join(EG_DIR, 'dotted.pdf'), 'rb'))

    pdf_files = sorted([f for f in os.listdir(FINAL_DIR) if f.endswith('pdf')])
    for f in pdf_files:
        merger.append(PdfReader(os.path.join(FINAL_DIR, f), 'rb'))

    for i in range(3):
        merger.append(
            PdfReader(os.path.join(EG_DIR, 'gridded.pdf'), 'rb'))
        merger.append(
            PdfReader(os.path.join(EG_DIR, 'dotted.pdf'), 'rb'))
    merger.write(OUTPUT_FILE)
    cleanup()
