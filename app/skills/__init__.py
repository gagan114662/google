# This package contains "skills" which are higher-level functions
# that orchestrate calls to one or more "tools" to achieve a specific capability.

# For example:
from .web_research import skill_extract_text_from_url, skill_perform_basic_search
from .reporting import skill_create_simple_text_report, skill_create_simple_pdf_report

# This helps in creating more complex agent behaviors by composing tools.
