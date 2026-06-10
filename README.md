# eCourt Case Information Scraper

A Scrapy-based web scraper that extracts case information and complete case history from the Indian eCourts portal.

## Features

- Fetches case details using Case Number
- Downloads captcha image automatically
- Manual captcha entry support
- Extracts:
  - Case Type
  - CNR Number
  - Case Status
  - Complete Case History
- Saves data in JSON format

## Tech Stack

- Python 3.12
- Scrapy
- XPath
- JSON

## Project Structure

```text
ecourt_scraper/
│
├── ecourt_scraper/
│   ├── spiders/
│   │   └── e_court_case_information.py
│   ├── settings.py
│   └── items.py
│
├── output.json
├── requirements.txt
├── scrapy.cfg
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Run Spider

```bash
scrapy crawl e_court_case_information
```

## Output

The scraper generates:

```json
{
    "case_type": "MACT - M.A.C.T.",
    "cnr": "DLSH010013732016",
    "status": "Case disposed",
    "history": []
}
```

## Author

Zuhaib Khan