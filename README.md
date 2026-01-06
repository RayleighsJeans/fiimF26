# Freitag Agenda Generator

A LaTeX-based agenda/planner generator with support for both daily and weekly layouts.

## Features

- **Weekly Mode (Default)**: Portrait orientation with 2 pages per week (Mon-Wed, Thu-Sun)
- **Daily Mode**: Portrait orientation with 4 days per page
- **Calendar Mode**: Generate calendar pages
- **Merge Mode**: Combine all generated PDFs
- Maintains existing `\sotapage` functionality for custom layouts
- Automatic calendar generation
- PDF merging with custom inlays

## Usage

### Weekly Mode (Default)
Generate agenda with 2 portrait pages per week (Mon-Wed on first page, Thu-Sun on second):
```bash
python3 constructor.py
# or explicitly:
python3 constructor.py --mode week
```

### Daily Mode
Generate agenda with 4 days per portrait page:
```bash
python3 constructor.py --mode day
```

### Calendar Mode
Generate calendar pages only:
```bash
python3 constructor.py --mode calendar
```

### Merge Mode
Merge all generated PDFs:
```bash
python3 constructor.py --mode merge
```

## Configuration

Edit `config.json` to set date ranges:
```json
{
    "author": "Your Name",
    "first_day": "1 1 2026",
    "last_day": "3 1 2027",
    "calendar_first": "1 1 2026",
    "calendar_last": "1 1 2028"
}
```

## Layout Details

### Weekly Mode
- **Orientation**: Portrait (120mm × 180mm)
- **Pages per week**: 2
  - Page 1: Monday, Tuesday, Wednesday
  - Page 2: Thursday, Friday, Saturday, Sunday
- **Template**: `agendaPageWeek.tex`
- Uses `\weekpage` command for the entire week
- Generates files named `week-YYYY-WW.txt.pdf`

### Daily Mode
- **Orientation**: Portrait (120mm × 180mm)
- **Days per page**: 4
- **Template**: `agendaPage.tex`
- Uses `\sotapage` command for each day

## Files

- `constructor.py` - Main build script with CLI interface
- `agendaPage.tex` - Daily layout template (portrait, 4 days)
- `agendaPageWeek.tex` - Weekly layout template (portrait, 2 pages per week)
- `agendaWeek.tex` - Weekly inlay assembly template
- `agenda.tex` - Daily inlay assembly template
- `calendarPage.tex` - Calendar page template
- `freitag.sty` - Page dimension and style definitions
- `inlay.sty` - PDF inclusion utilities
- `config.json` - Date range configuration
- `utils.py` - Utility functions (e.g., LaTeX escaping)

## Output

The script generates:
- Individual page definition files in `tmp/` directory
- Compiled page PDFs in `pdf/` directory
- Final merged PDFs in `final/` directory:
  - `final/output.pdf` - Complete merged agenda
  - Individual week/day PDFs as needed

## Requirements

- Python 3
- pdflatex (TeX Live or similar)
- Python packages: `python-dateutil`, `PyPDF2`

Install Python dependencies:
```bash
pip install -r requirements.txt