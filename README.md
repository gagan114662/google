# Project Chimera - Core API & Local Task Runner

This repository contains the backend Core API for Project Chimera, an open-source autonomous agent platform, as well as a local task runner for demonstrating and testing agent capabilities.

Refer to the `Product Requirements Document (PRD) Project Chimera.md` for the full project vision, architecture, and requirements.

## Current Stage: Foundational Local Tools

The project is currently focused on building out foundational "tools" and "skills" that agents can use, with an emphasis on local execution and testing without requiring full API infrastructure or external service authentications yet.

## Components

*   **`app/`**: Contains the FastAPI backend application code (though not fully utilized by the local runner yet).
    *   **`app/api/`**: API endpoint definitions.
    *   **`app/core/`**: Core configuration (database, Redis - primarily for the API).
    *   **`app/models/`**: Database models.
    *   **`app/services/`**: Business logic for the API (placeholder).
    *   **`app/tools/`**: Low-level capabilities for agents:
        *   `web_scraper.py`: Basic web fetching (static via `requests`), parsing, and simulated search. Also includes **dynamic web fetching** (via `Botasaurus`), dynamic search (experimental), and screenshot capture.
        *   `file_system.py`: Reading and writing files to a local `workspace/` directory.
        *   `content_generator.py`: Creating text files, simple PDFs, and Excel spreadsheets.
    *   **`app/skills/`**: Higher-level functions composing tools:
        *   `web_research.py`: Skills for extracting text from URLs (static and dynamic), performing searches (static and dynamic).
        *   `reporting.py`: Skills for generating simple reports.
*   **`run_task.py`**: A command-line script for running predefined local "agent" tasks that demonstrate the use of tools and skills.
*   **`workspace/`**: A directory created at runtime by `run_task.py` for any input/output files used by tasks. It is cleaned before each run.
*   **`AGENTS.md`**: Guidelines for AI agents (and human developers) working on this codebase.
*   **`requirements.txt`**: Python dependencies.

## Running Local Tasks with `run_task.py`

The `run_task.py` script allows you to execute predefined tasks locally to test the implemented tools and skills.

### Prerequisites

1.  **Python 3.11+**
2.  **Virtual Environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    (Note: PostgreSQL and Redis are listed in `AGENTS.md` for the full API setup but are not strictly required for `run_task.py` unless a task specifically tries to use API core components, which current tasks do not.)

### Usage

```bash
python run_task.py <task_name>
```

### Available Tasks

*   **`example`**: A simple placeholder task that demonstrates the orchestration flow.
*   **`excel_lotto`**: Generates an Excel file (`workspace/italian_lottery_games.xlsx`) with information about Italian lottery games.
*   **`dynamic_scrape_test`**: Tests dynamic web scraping using Botasaurus. Fetches content from a JS-reliant site (`http://quotes.toscrape.com/js/`), saves it, performs a dynamic search, and takes a screenshot. **Requires `xvfb-run` to execute properly in headless environments.**

### Usage Examples

**Basic Task:**
```bash
python run_task.py excel_lotto
```
This will create the `workspace` directory (if it doesn't exist, or clean it if it does), run the `excel_lotto` task, and output status messages. The resulting Excel file will be in `workspace/italian_lottery_games.xlsx`.

**Task Requiring Dynamic Scraping (needs Xvfb):**
```bash
xvfb-run -a python run_task.py dynamic_scrape_test
```

## Development of the FastAPI Backend

```bash
python run_task.py excel_lotto
```
This will create the `workspace` directory (if it doesn't exist, or clean it if it does), run the `excel_lotto` task, and output status messages. The resulting Excel file will be in `workspace/italian_lottery_games.xlsx`.

## Development of the FastAPI Backend

Instructions for setting up and running the full FastAPI backend (which is separate from the local `run_task.py` execution) can be found in `AGENTS.md`.

## Contributing

Please refer to `AGENTS.md` for initial coding conventions and guidelines. More detailed contribution guidelines will be added as the project matures.
---

This README provides a starting point and will be expanded as the project develops.
