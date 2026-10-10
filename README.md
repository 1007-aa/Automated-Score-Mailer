# Automated Score Mailer

A robust automation tool that reads student rank and score data from Excel sheets, generates personalized performance charts, and emails customized HTML reports to parents/students. 
It also includes a Google Apps Script version for direct Google Sheets integration.

## Features
- **Data Processing:** Extracts data directly from Excel files.
- **Chart Generation:** Uses Matplotlib to generate custom performance comparison charts (Student vs. Class Average).
- **Automated HTML Emails:** Sends out beautiful HTML emails with embedded charts.
- **Apps Script Alternative:** Includes `.gs` code and HTML template to run directly from Google Sheets.

## Prerequisites
- Python 3.11+
- A Gmail account with an App Password (if using the Python version).

## Setup (Python Version)
1. Clone the repository and navigate to the project directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configure your credentials by copying `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Add your Gmail address and App Password.

## Usage
1. Place your input Excel data in the `input_data/` folder.
2. Run the main script:
   ```bash
   python main.py
   ```

## Google Apps Script Usage
You can alternatively use the code inside the `apps_script/` folder.
1. Copy the contents of `Code.gs` into the Apps Script editor of your Google Sheet.
2. Create an HTML file named `emailTemplate.html` in the Apps Script editor and paste the contents from the repository.
3. Run the script directly from the editor or create a custom menu in Google Sheets.
