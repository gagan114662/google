# This package contains various tools that the agent can use.
# For example: web_scraper, file_system, content_generator

from .web_scraper import fetch_html, parse_html_to_text, search_google
from .file_system import read_file, write_file, list_files
from .content_generator import (
    generate_text_report,
    generate_pdf_report_simple,
    create_excel_spreadsheet,
    generate_summary_placeholder,
    generate_email_draft_placeholder
)
# Add other tool imports as they are created
