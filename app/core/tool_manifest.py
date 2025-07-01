"""
Tool and Skill Manifest for Project Chimera.
This manifest describes the available tools and skills to an LLM,
allowing it to generate execution plans.
"""

# The manifest is a list of dictionaries, each describing a tool or skill.
TOOL_MANIFEST = [
    # --- Web Scraper Tools (app.tools.web_scraper) ---
    {
        "name": "app.tools.web_scraper.fetch_html",
        "description": "Fetches the static HTML content from a given URL using a simple HTTP request. Does not execute JavaScript.",
        "parameters": [
            {"name": "url", "type": "str", "description": "The URL to fetch HTML from.", "required": True},
            {"name": "timeout", "type": "int", "description": "Maximum time in seconds to wait for a response.", "required": False, "default": 10},
        ],
        "returns": {"type": "str | None", "description": "The HTML content as a string, or None if an error occurs."}
    },
    {
        "name": "app.tools.web_scraper.parse_html_to_text",
        "description": "Parses HTML content and extracts human-readable text. Removes script/style tags and cleans whitespace.",
        "parameters": [
            {"name": "html_content", "type": "str", "description": "The HTML content string to parse.", "required": True},
        ],
        "returns": {"type": "str", "description": "The extracted plain text."}
    },
    {
        "name": "app.tools.web_scraper.fetch_html_dynamic",
        "description": "Fetches HTML content from a given URL after JavaScript execution using a browser automation tool (Botasaurus). Use this for dynamic websites.",
        "parameters": [
            {"name": "url", "type": "str", "description": "The URL to fetch dynamic HTML from.", "required": True},
            {"name": "timeout", "type": "int", "description": "General timeout guideline in seconds for the operation.", "required": False, "default": 30},
        ],
        "returns": {"type": "str | None", "description": "The HTML content as a string after JS execution, or None if an error occurs."}
    },
    {
        "name": "app.tools.web_scraper.capture_screenshot_dynamic",
        "description": "Captures a screenshot of a webpage after JavaScript execution using Botasaurus. Saves to workspace/output_filename.",
        "parameters": [
            {"name": "url", "type": "str", "description": "The URL to capture a screenshot of.", "required": True},
            {"name": "output_filename", "type": "str", "description": "The filename for the screenshot (e.g., 'page.png'). It will be saved in the 'workspace/' directory.", "required": True},
        ],
        "returns": {"type": "bool", "description": "True if successful, False otherwise."}
    },
    {
        "name": "app.tools.web_scraper.search_google_dynamic",
        "description": "(EXPERIMENTAL) Performs a Google search using dynamic HTML fetching (Botasaurus) and attempts to parse results. Highly unreliable due to Google's anti-scraping.",
        "parameters": [
            {"name": "query", "type": "str", "description": "The search query.", "required": True},
            {"name": "num_results", "type": "int", "description": "Desired number of results.", "required": False, "default": 5},
        ],
        "returns": {"type": "list[dict]", "description": "A list of search result dictionaries (keys: 'title', 'link', 'snippet'), or an empty list on failure."}
    },
    {
        "name": "app.tools.web_scraper.search_google",
        "description": "(EXPERIMENTAL) Performs a Google search using static HTML fetching and attempts to parse results. Very unreliable.",
        "parameters": [
            {"name": "query", "type": "str", "description": "The search query.", "required": True},
            {"name": "num_results", "type": "int", "description": "Desired number of results.", "required": False, "default": 5},
        ],
        "returns": {"type": "list[dict]", "description": "A list of search result dictionaries (keys: 'title', 'link', 'snippet'), or an empty list on failure."}
    },

    # --- File System Tools (app.tools.file_system) ---
    {
        "name": "app.tools.file_system.read_file",
        "description": "Reads content from a file in the 'workspace/' directory. Filepath is relative to 'workspace/'.",
        "parameters": [
            {"name": "filepath", "type": "str", "description": "Path to the file relative to the 'workspace/' directory.", "required": True},
        ],
        "returns": {"type": "str | None", "description": "Content as a string, or None if an error occurs."}
    },
    {
        "name": "app.tools.file_system.write_file",
        "description": "Writes content to a file in the 'workspace/' directory. Filepath is relative to 'workspace/'. Creates subdirectories if they don't exist.",
        "parameters": [
            {"name": "filepath", "type": "str", "description": "Path to the file relative to the 'workspace/' directory.", "required": True},
            {"name": "content", "type": "str", "description": "The content to write.", "required": True},
        ],
        "returns": {"type": "bool", "description": "True if successful, False otherwise."}
    },
    {
        "name": "app.tools.file_system.list_files",
        "description": "Lists all files and directories within the given path relative to 'workspace/'. Default path is the root of 'workspace/'.",
        "parameters": [
            {"name": "dirpath", "type": "str", "description": "Directory path relative to 'workspace/'. Defaults to '.' (workspace root).", "required": False, "default": "."},
        ],
        "returns": {"type": "list[str]", "description": "List of relative paths. Directories have a trailing slash."}
    },

    # --- Content Generator Tools (app.tools.content_generator) ---
    {
        "name": "app.tools.content_generator.generate_text_report",
        "description": "Creates a simple .txt report in the 'workspace/' directory.",
        "parameters": [
            {"name": "filename", "type": "str", "description": "Filename for the report (e.g., 'my_report.txt'), relative to 'workspace/'.", "required": True},
            {"name": "title", "type": "str", "description": "Title of the report.", "required": True},
            {"name": "content", "type": "str", "description": "Main content of the report.", "required": True},
        ],
        "returns": {"type": "bool", "description": "True if successful, False otherwise."}
    },
    {
        "name": "app.tools.content_generator.generate_pdf_report_simple",
        "description": "Creates a basic PDF report in 'workspace/' using ReportLab.",
        "parameters": [
            {"name": "filename", "type": "str", "description": "Filename for the PDF report (e.g., 'report.pdf'), relative to 'workspace/'.", "required": True},
            {"name": "title", "type": "str", "description": "Title of the PDF report.", "required": True},
            {"name": "text_content", "type": "list[str]", "description": "A list of strings, each representing a paragraph for the PDF.", "required": True},
        ],
        "returns": {"type": "bool", "description": "True if successful, False otherwise."}
    },
    {
        "name": "app.tools.content_generator.create_excel_spreadsheet",
        "description": "Creates an .xlsx file in 'workspace/' using openpyxl.",
        "parameters": [
            {"name": "filename", "type": "str", "description": "Filename for the Excel sheet (e.g., 'data.xlsx'), relative to 'workspace/'.", "required": True},
            {"name": "data", "type": "list[list[any]]", "description": "A list of lists, where each inner list is a row of data.", "required": True},
            {"name": "headers", "type": "list[str]", "description": "Optional list of strings for the first (header) row.", "required": False, "default": None},
        ],
        "returns": {"type": "bool", "description": "True if successful, False otherwise."}
    },
    {
        "name": "app.tools.content_generator.generate_summary_local_llm",
        "description": "Generates a summary of the given text using a local LLM (via Ollama). Falls back to truncation if Ollama is unavailable or fails.",
        "parameters": [
            {"name": "text_to_summarize", "type": "str", "description": "The text to be summarized.", "required": True},
            {"name": "max_length", "type": "int", "description": "Approximate target maximum length for the summary (in characters).", "required": False, "default": 150},
            {"name": "custom_system_prompt", "type": "str", "description": "Optional custom system prompt to override the default for summarization. Can use {max_length}.", "required": False, "default": None},
        ],
        "returns": {"type": "str | None", "description": "The generated summary string, or None/truncated if LLM fails."}
    },
    {
        "name": "app.tools.content_generator.generate_email_draft_local_llm",
        "description": "Generates an email draft using a local LLM (via Ollama). Falls back to a placeholder if LLM fails.",
        "parameters": [
            {"name": "to", "type": "str", "description": "Recipient's email (for LLM context).", "required": True},
            {"name": "subject", "type": "str", "description": "Desired subject of the email.", "required": True},
            {"name": "body_prompt", "type": "str", "description": "A prompt describing the desired content/purpose of the email body.", "required": True},
            {"name": "email_type", "type": "str", "description": "A hint for the LLM about email style (e.g., 'professional first contact').", "required": False, "default": "professional first contact"},
        ],
        "returns": {"type": "dict", "description": "A dictionary {'to': to, 'subject': subject, 'body': generated_body_text} or a placeholder."}
    },

    # --- Web Research Skills (app.skills.web_research) ---
    {
        "name": "app.skills.web_research.skill_extract_text_from_url",
        "description": "Fetches HTML from a URL (statically or dynamically) and extracts readable text content.",
        "parameters": [
            {"name": "url", "type": "str", "description": "The URL to extract text from.", "required": True},
            {"name": "use_dynamic_fetch", "type": "bool", "description": "Set to True to use dynamic fetching (Botasaurus) for JS-heavy sites.", "required": False, "default": False},
        ],
        "returns": {"type": "str | None", "description": "The extracted text content, or None if an error occurs."}
    },
    {
        "name": "app.skills.web_research.skill_perform_basic_search",
        "description": "(EXPERIMENTAL) Performs a basic web search using the static (requests-based) Google search tool. Very unreliable.",
        "parameters": [
            {"name": "query", "type": "str", "description": "The search query.", "required": True},
            {"name": "num_results", "type": "int", "description": "Desired number of results.", "required": False, "default": 3},
        ],
        "returns": {"type": "list[dict]", "description": "List of search results {'title', 'link'}, or empty list."}
    },
    {
        "name": "app.skills.web_research.skill_perform_dynamic_search",
        "description": "(EXPERIMENTAL) Performs a web search using the dynamic (Botasaurus-based) Google search tool. Highly unreliable.",
        "parameters": [
            {"name": "query", "type": "str", "description": "The search query.", "required": True},
            {"name": "num_results", "type": "int", "description": "Desired number of results.", "required": False, "default": 3},
        ],
        "returns": {"type": "list[dict]", "description": "List of search results {'title', 'link', 'snippet'}, or empty list."}
    },

    # --- Reporting Skills (app.skills.reporting) ---
    {
        "name": "app.skills.reporting.skill_create_simple_text_report",
        "description": "Generates a simple text report and saves it to the 'workspace/'.",
        "parameters": [
            {"name": "report_title", "type": "str", "description": "Title for the report.", "required": True},
            {"name": "report_body_content", "type": "str", "description": "Main content for the report body.", "required": True},
            {"name": "output_filename", "type": "str", "description": "Filename for the report (e.g., 'my_report.txt'). Will be saved in 'workspace/'.", "required": False, "default": "report.txt"},
        ],
        "returns": {"type": "str | None", "description": "Relative filepath of the generated report if successful, else None."}
    },
    {
        "name": "app.skills.reporting.skill_create_simple_pdf_report",
        "description": "Generates a simple PDF report and saves it to the 'workspace/'.",
        "parameters": [
            {"name": "report_title", "type": "str", "description": "Title for the PDF report.", "required": True},
            {"name": "paragraphs", "type": "list[str]", "description": "A list of strings, each a paragraph for the PDF.", "required": True},
            {"name": "output_filename", "type": "str", "description": "Filename for the PDF (e.g., 'my_report.pdf'). Will be saved in 'workspace/'.", "required": False, "default": "report.pdf"},
        ],
        "returns": {"type": "str | None", "description": "Relative filepath of the generated PDF report if successful, else None."}
    },
    # Future tools like edit_text_file_descriptively_local_llm would be added here
]

def get_tool_manifest() -> list[dict]:
    """Returns the global tool manifest."""
    return TOOL_MANIFEST

if __name__ == "__main__":
    # Quick test to print the manifest or count tools
    manifest = get_tool_manifest()
    print(f"Loaded Tool Manifest with {len(manifest)} tools/skills.")
    # import json
    # print(json.dumps(manifest, indent=2))
    for tool_def in manifest:
        print(f"- {tool_def['name']}")
        for param in tool_def['parameters']:
            print(f"  - {param['name']} ({param['type']}) {'[OPTIONAL]' if not param['required'] else ''}")

        print(f"  -> Returns: {tool_def['returns']['type']} ({tool_def['returns']['description']})")
        print("-" * 20)
    # Example: Find a tool
    # tool_name_to_find = "app.tools.file_system.write_file"
    # found = next((t for t in manifest if t["name"] == tool_name_to_find), None)
    # if found:
    #     print(f"\nFound tool: {tool_name_to_find}")
    #     print(json.dumps(found, indent=2))
