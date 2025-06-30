import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook

# Tools should operate relative to this base or expect absolute paths within it.
# This should align with file_system.py and run_task.py
WORKSPACE_DIR = "workspace"

def _get_safe_workspace_path(filename: str) -> str:
    """
    Ensures the path is within the WORKSPACE_DIR and resolves it.
    Prevents directory traversal. Used for output files.
    """
    base_path = os.path.abspath(WORKSPACE_DIR)
    # Ensure filename is relative before joining, to avoid issues if it's absolute
    if os.path.isabs(filename):
        # This case should ideally not happen if tools always pass relative paths
        # but as a safeguard:
        raise ValueError("content_generator expects relative filenames for output.")

    target_path = os.path.abspath(os.path.join(base_path, filename))

    if os.path.commonprefix([target_path, base_path]) != base_path:
        raise ValueError(f"Attempted file access outside workspace: {filename}")

    # Create parent directories if they don't exist
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    return target_path

def generate_text_report(filename: str, title: str, content: str) -> bool:
    """
    Creates a simple .txt report in the WORKSPACE_DIR.
    filename is relative to the WORKSPACE_DIR.
    """
    safe_filepath = _get_safe_workspace_path(filename)
    print(f"  [ContentGenerator] Generating text report: {safe_filepath}")
    try:
        full_content = f"Title: {title}\n\n{content}"
        with open(safe_filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        print(f"  [ContentGenerator] Text report generated: {safe_filepath}")
        return True
    except Exception as e:
        print(f"  [ContentGenerator] Error generating text report {safe_filepath}: {e}")
        return False

def generate_pdf_report_simple(filename: str, title: str, text_content: list[str]) -> bool:
    """
    Creates a basic PDF report in WORKSPACE_DIR using ReportLab.
    filename is relative to the WORKSPACE_DIR.
    text_content is a list of strings, each representing a paragraph.
    """
    safe_filepath = _get_safe_workspace_path(filename)
    print(f"  [ContentGenerator] Generating PDF report: {safe_filepath}")
    try:
        doc = SimpleDocTemplate(safe_filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph(title, styles['h1']))
        story.append(Spacer(1, 12)) # 12 points of space

        # Content paragraphs
        for paragraph_text in text_content:
            story.append(Paragraph(paragraph_text, styles['Normal']))
            story.append(Spacer(1, 6)) # 6 points of space after each paragraph

        doc.build(story)
        print(f"  [ContentGenerator] PDF report generated: {safe_filepath}")
        return True
    except Exception as e:
        print(f"  [ContentGenerator] Error generating PDF report {safe_filepath}: {e}")
        return False

def create_excel_spreadsheet(filename: str, data: list[list[any]], headers: list[str] = None) -> bool:
    """
    Creates an .xlsx file in WORKSPACE_DIR using openpyxl.
    filename is relative to the WORKSPACE_DIR.
    data is a list of lists, where each inner list is a row.
    headers is an optional list of strings for the first row.
    """
    safe_filepath = _get_safe_workspace_path(filename)
    print(f"  [ContentGenerator] Creating Excel spreadsheet: {safe_filepath}")
    try:
        wb = Workbook()
        ws = wb.active # Get the default sheet

        if headers:
            ws.append(headers)

        for row_data in data:
            ws.append(row_data)

        wb.save(safe_filepath)
        print(f"  [ContentGenerator] Excel spreadsheet created: {safe_filepath}")
        return True
    except Exception as e:
        print(f"  [ContentGenerator] Error creating Excel spreadsheet {safe_filepath}: {e}")
        return False

# Placeholder functions for more complex text generation (summaries, emails)
def generate_summary_placeholder(text_to_summarize: str, max_length: int = 150) -> str:
    """
    Placeholder for a text summarization function.
    Currently returns a truncated version of the original text.
    """
    print("  [ContentGenerator] Generating summary (placeholder)...")
    if not text_to_summarize:
        return ""
    summary = text_to_summarize[:max_length]
    if len(text_to_summarize) > max_length:
        summary += "..."
    return summary

def generate_email_draft_placeholder(to: str, subject: str, body_prompt: str) -> dict:
    """
    Placeholder for an email drafting function.
    Currently returns a canned email structure.
    """
    print("  [ContentGenerator] Generating email draft (placeholder)...")
    return {
        "to": to,
        "subject": f"Regarding: {subject}",
        "body": f"Dear recipient,\n\nThis is a placeholder email draft based on the prompt: '{body_prompt}'.\n\nFurther content would be generated here by a more advanced model.\n\nSincerely,\nChimera Agent"
    }


if __name__ == '__main__':
    print("--- Testing Content Generator Tools ---")

    # Setup a dummy workspace for testing this module directly
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)

    # Test generate_text_report
    print("\nTesting generate_text_report...")
    txt_success = generate_text_report(
        "sample_report.txt",
        "My Text Report",
        "This is the main content of the text report.\nIt spans multiple lines."
    )
    print(f"Text report generation successful: {txt_success}")
    if txt_success:
        assert os.path.exists(os.path.join(WORKSPACE_DIR, "sample_report.txt"))

    # Test generate_pdf_report_simple
    print("\nTesting generate_pdf_report_simple...")
    pdf_content = [
        "This is the first paragraph of our simple PDF report.",
        "It demonstrates the basic capability to generate PDF documents using ReportLab.",
        "Each item in this list becomes a new paragraph."
    ]
    pdf_success = generate_pdf_report_simple(
        "sample_report.pdf",
        "My Simple PDF Report",
        pdf_content
    )
    print(f"PDF report generation successful: {pdf_success}")
    if pdf_success:
        assert os.path.exists(os.path.join(WORKSPACE_DIR, "sample_report.pdf"))

    # Test create_excel_spreadsheet
    print("\nTesting create_excel_spreadsheet...")
    excel_data = [
        ["Alice", 30, "Engineer"],
        ["Bob", 24, "Artist"],
        ["Charlie", 35, "Manager"]
    ]
    excel_headers = ["Name", "Age", "Occupation"]
    excel_success = create_excel_spreadsheet(
        "sample_sheet.xlsx",
        excel_data,
        headers=excel_headers
    )
    print(f"Excel spreadsheet generation successful: {excel_success}")
    if excel_success:
        assert os.path.exists(os.path.join(WORKSPACE_DIR, "sample_sheet.xlsx"))

    # Test placeholder functions
    print("\nTesting generate_summary_placeholder...")
    long_text = "This is a very long string of text that is intended to be summarized by the placeholder function. It keeps going and going to ensure it's longer than the max length."
    summary = generate_summary_placeholder(long_text)
    print(f"Generated summary: {summary}")

    print("\nTesting generate_email_draft_placeholder...")
    email = generate_email_draft_placeholder("test@example.com", "Meeting Follow-up", "Discuss project X details")
    print(f"Generated email: {email}")

    print("\n--- Content Generator Test Complete ---")
    # import shutil
    # if os.path.exists(WORKSPACE_DIR):
    #     shutil.rmtree(WORKSPACE_DIR)
