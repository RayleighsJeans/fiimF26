# Freitag Agenda Generator

A LaTeX-based agenda/planner generator with support for both daily and weekly layouts.

## Features

- **Daily Mode (Default)**: Portrait orientation with 4 days per page
- **Weekly Mode**: Landscape orientation with 7 days per week (5 larger business days + 2 smaller weekend days)
- Maintains existing `\sotapage` functionality for custom layouts
- Automatic calendar generation
- PDF merging with custom inlays

## Usage

### Daily Mode (Default)
Generate agenda with 4 days per portrait page:
```bash
python3 constructor.py
```

### Weekly Mode
Generate agenda with 7 days per landscape page:
```bash
python3 constructor.py --mode week
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

### Daily Mode
- **Orientation**: Portrait (120mm × 180mm)
- **Days per page**: 4
- **Template**: `agendaPage.tex`
- Uses `\sotapage` command for each day

### Weekly Mode
- **Orientation**: Landscape (180mm × 120mm)
- **Days per page**: 7 (full week)
- **Template**: `agendaPageWeek.tex`
- **Business days** (Mon-Fri): Larger columns
- **Weekend days** (Sat-Sun): Smaller columns with shaded background
- Uses `\weekpage` command for the entire week

## Files

- `constructor.py` - Main build script with CLI interface
- `agendaPage.tex` - Daily layout template (portrait, 4 days)
- `agendaPageWeek.tex` - Weekly layout template (landscape, 7 days)
- `agenda.tex` - PDF assembly template
- `calendarPage.tex` - Calendar page template
- `freitag.sty` - Page dimension and style definitions
- `inlay.sty` - PDF inclusion utilities
- `config.json` - Date range configuration

## Output

The script generates:
- Individual page PDFs in `tmp/` directory
- Compiled pages in `pdf/` directory
- Final merged PDF as `output.pdf`

## Requirements

- Python 3
- pdflatex (TeX Live or similar)
- Python packages: `python-dateutil`, `PyPDF2`

Install Python dependencies:
```bash
pip install -r requirements.txt