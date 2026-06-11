# eCourt Case Information Scraper

## Overview

This project is a Scrapy-based web scraper developed to extract case information from the Indian eCourts portal.

The scraper performs the following tasks:

* Solves and submits captcha requests.
* Searches case information using case details.
* Extracts case metadata.
* Extracts hearing history.
* Extracts petitioner and respondent information.
* Extracts act and section details.
* Detects and processes available court documents.
* Downloads PDF documents.
* Stores extracted data in JSON format.

---

## GitHub Repository

https://github.com/Zuhaibkhank/ecourt-case-information-scraper

## Features

### Case Information Extraction

The scraper extracts:

* Case Type
* Filing Number
* Filing Date
* Registration Number
* Registration Date
* CNR Number
* First Hearing Date
* Decision Date
* Case Status
* Nature of Disposal
* Court and Judge Information

### Party Details

* Petitioner
* Respondent

### Legal Details

* Act
* Section

### Hearing History

For each hearing:

* Judge Name
* Business Date
* Hearing Date
* Purpose

### Document Processing

* Detects available orders and proceedings
* Downloads PDF files
* Saves PDFs locally in the `documents` directory

### JSON Export

All extracted information is stored in:

```text
output.json
```

---

## Project Structure

```text
ecourt_scraper/
│
├── documents/
│   ├── document_1.pdf
│   ├── document_2.pdf
│   └── ...
│
├── ecourt_scraper/
│   ├── spiders/
│   │   └── e_court_case_information.py
│   ├── items.py
│   ├── pipelines.py
│   ├── settings.py
│   └── middlewares.py
│
├── output.json
├── requirements.txt
├── scrapy.cfg
└── README.md
```

---

## Installation

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Scraper

```bash
scrapy crawl e_court_case_information
```

---

## Output

### JSON Output

```text
output.json
```

Contains:

* Case Details
* Hearing History
* Party Information
* Legal Information
* Document Metadata

### PDF Output

```text
documents/
```

Contains downloaded PDF files related to the case.

---

## Technologies Used

* Python 3
* Scrapy
* XPath
* JSON
* Requests Handling
* PDF Processing

---

## Notes

* The scraper creates required directories automatically.
* Extracted data is saved in structured JSON format.
* PDF files are stored separately in the documents folder.
* Logging information is displayed in the terminal during execution.

---

## Author

Zuhaib Khan
