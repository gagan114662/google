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

# --- LLM Integration ---
from app.llm import ollama_client, OLLAMA_IS_AVAILABLE, get_default_model_name
import logging

logger = logging.getLogger(__name__)
# --- End LLM Integration ---

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
    if not OLLAMA_IS_AVAILABLE():
        logger.warning("Ollama not available. Falling back to placeholder summary (truncation).")
        summary = text_to_summarize[:max_length]
        if len(text_to_summarize) > max_length and len(text_to_summarize) > 0:
            summary += "..."
        return summary

    system_prompt_summary = "You are an expert summarization assistant. Summarize the following text concisely, capturing the main points. The summary should be approximately {max_length} characters or less if possible, but prioritize clarity."
    prompt = f"Please summarize the following text:\n\n---\n{text_to_summarize}\n---\n\nSummary:"

    model_to_use = get_default_model_name()
    logger.info(f"  [ContentGenerator] Requesting summary from Ollama model: {model_to_use}")

    summary = ollama_client.generate_text(
        prompt=prompt,
        model_name=model_to_use,
        system_prompt=system_prompt_summary.format(max_length=max_length),
        temperature=0.3 # Lower temperature for more factual summaries
    )

    if summary:
        logger.info(f"  [ContentGenerator] Summary received from LLM.")
        # Optional: could try to enforce max_length post-generation if needed, but prompt is better
        return summary.strip()
    else:
        logger.warning("  [ContentGenerator] LLM summary generation failed. Falling back to truncation.")
        summary = text_to_summarize[:max_length]
        if len(text_to_summarize) > max_length and len(text_to_summarize) > 0:
            summary += "..."
        return summary


def generate_email_draft_local_llm(to: str, subject: str, body_prompt: str, email_type: str = "professional first contact") -> dict:
    """
    Generates an email draft using a local LLM via Ollama.
    Args:
        to: Recipient's email (for context, not used by LLM directly for sending).
        subject: Desired subject of the email.
        body_prompt: A prompt describing the desired content or purpose of the email body.
                     Example: "Client is a cleantech company. Introduce our consulting services focused on profit maximization and cost reduction."
        email_type: A hint for the LLM about the email style (e.g., "professional first contact", "follow-up", "thank you").

    Returns:
        A dictionary {"to": to, "subject": subject, "body": generated_body_text}
        or a placeholder if LLM fails or is unavailable.
    """
    print(f"  [ContentGenerator] Generating email draft for '{to}' with subject '{subject}' (LLM)...")

    if not OLLAMA_IS_AVAILABLE():
        logger.warning("Ollama not available. Falling back to placeholder email draft.")
        return {
            "to": to,
            "subject": f"[Placeholder] Regarding: {subject}",
            "body": f"Dear recipient,\n\nThis is a placeholder email draft based on the prompt: '{body_prompt}'.\nOllama was not available to generate this email.\n\nSincerely,\nChimera Agent (Local Fallback)"
        }

    system_prompt_email = f"You are an expert email writing assistant. Your task is to draft a compelling and {email_type} email. Ensure the tone is appropriate and the message is clear and concise."

    full_prompt = (
        f"Draft the body of a {email_type} email.\n"
        f"Recipient context (do not include email address in body unless asked): {to}\n"
        f"Desired Subject (for context, generate body only): {subject}\n"
        f"Key points or purpose for the email body (elaborate on this): {body_prompt}\n\n"
        f"Email Body:"
    )

    model_to_use = get_default_model_name()
    logger.info(f"  [ContentGenerator] Requesting email body from Ollama model: {model_to_use}")

    email_body = ollama_client.generate_text(
        prompt=full_prompt,
        model_name=model_to_use,
        system_prompt=system_prompt_email,
        temperature=0.7 # Slightly higher for more natural language
    )

    if email_body:
        logger.info("  [ContentGenerator] Email body received from LLM.")
        return {
            "to": to,
            "subject": subject, # Use the user-provided subject
            "body": email_body.strip()
        }
    else:
        logger.warning("  [ContentGenerator] LLM email generation failed. Falling back to placeholder.")
        return {
            "to": to,
            "subject": f"[Placeholder - LLM Failed] Regarding: {subject}",
            "body": f"Dear recipient,\n\nThis is a placeholder email draft. LLM generation failed based on prompt: '{body_prompt}'.\n\nSincerely,\nChimera Agent (Local Fallback)"
        }


if __name__ == '__main__':
    # Configure basic logging for direct script testing
    logging.basicConfig(level=logging.INFO)
    logger.info("--- Testing Content Generator Tools (with Local LLM integration) ---")
    # Reminder for users running this directly:
    logger.info("NOTE: For LLM tests to run live, ensure Ollama service is running and a model (e.g., orca-mini or your DEFAULT_OLLAMA_MODEL) is pulled.")
    logger.info(f"Using default model: {get_default_model_name()}. Ollama available: {OLLAMA_IS_AVAILABLE()}")

    # Setup a dummy workspace for testing this module directly
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)

    # Test generate_text_report
    logger.info("\nTesting generate_text_report...")
    txt_success = generate_text_report(
        "sample_report.txt",
        "My Text Report",
        "This is the main content of the text report.\nIt spans multiple lines."
    )
    logger.info(f"Text report generation successful: {txt_success}")
    if txt_success:
        assert os.path.exists(os.path.join(WORKSPACE_DIR, "sample_report.txt"))

    # Test generate_pdf_report_simple
    logger.info("\nTesting generate_pdf_report_simple...")
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
    logger.info(f"PDF report generation successful: {pdf_success}")
    if pdf_success:
        assert os.path.exists(os.path.join(WORKSPACE_DIR, "sample_report.pdf"))

    # Test create_excel_spreadsheet
    logger.info("\nTesting create_excel_spreadsheet...")
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
    logger.info(f"Excel spreadsheet generation successful: {excel_success}")
    if excel_success:
        assert os.path.exists(os.path.join(WORKSPACE_DIR, "sample_sheet.xlsx"))

    # Test LLM-based functions
    logger.info("\nTesting generate_summary_local_llm...")
    long_text_for_summary = (
        "The quick brown fox jumps over the lazy dog. This sentence is famous because it contains all letters of the English alphabet. "
        "It is often used for testing typewriters and keyboard layouts. The study of pangrams, sentences that contain every letter of the alphabet, "
        "is an interesting linguistic pursuit. Early versions of this pangram date back to the late 19th century."
    )
    summary = generate_summary_local_llm(long_text_for_summary, max_length=50)
    logger.info(f"Generated summary (target ~50 chars, model: {get_default_model_name()}):\n{summary}")
    if OLLAMA_IS_AVAILABLE() : # Only assert length if LLM was supposed to run
      if summary:
        assert len(summary) > 5 # Check it's not empty or trivial
        # Length assertion can be tricky with LLMs, prompt is a suggestion
        # assert len(summary) < 100
      else:
        logger.warning("Summary was None, check LLM interaction.")


    logger.info("\nTesting generate_email_draft_local_llm...")
    email_details = generate_email_draft_local_llm(
        to="potential_client@example.com",
        subject="Introducing Chimera Consulting Services",
        body_prompt="We are Chimera Corp, offering AI-driven solutions to optimize your business processes. We'd like to schedule a brief call to discuss how our expertise in automation and data analytics can help your company achieve its strategic goals for the next quarter.",
        email_type="professional introduction"
    )
    logger.info(f"Generated email (model: {get_default_model_name()}):")
    logger.info(f"To: {email_details['to']}")
    logger.info(f"Subject: {email_details['subject']}")
    logger.info(f"Body:\n{email_details['body']}")
    if OLLAMA_IS_AVAILABLE():
        if email_details['body']:
             assert len(email_details['body']) > 50 # Check for substantial body
        else:
            logger.warning("Email body was None/empty, check LLM interaction.")


    logger.info("\n--- Content Generator Test Complete ---")
    # import shutil
    # if os.path.exists(WORKSPACE_DIR):
    #     shutil.rmtree(WORKSPACE_DIR)
