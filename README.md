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
        *   `content_generator.py`: Creating text files, simple PDFs, and Excel spreadsheets. **Now includes local LLM integration (via Ollama) for text summarization and email drafting, with fallbacks.**
    *   **`app/skills/`**: Higher-level functions composing tools:
        *   `web_research.py`: Skills for extracting text from URLs (static and dynamic), performing searches (static and dynamic).
        *   `reporting.py`: Skills for generating simple reports.
    *   **`app/llm/`**: Client for interacting with local LLMs.
        *   `ollama_client.py`: Client for Ollama service.
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
*   **`local_llm_test_summary`**: Tests text summarization using a locally running Ollama model. **Requires Ollama to be running with a model (e.g., `deepseek-r1:8b` or `orca-mini:latest`).**

### Setup for Local LLM (Ollama)

To use the local LLM capabilities (like summarization or email drafting):

1.  **Install Ollama**: Follow instructions at [https://ollama.com](https://ollama.com). For Linux:
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
2.  **Pull a Model**: It's recommended to use a DeepSeek model for better quality. The `deepseek-r1:8b` model is a good balance, or `deepseek-r1:7b` / `deepseek-r1:1.5b` for lighter needs.
    ```bash
    ollama pull deepseek-r1:8b
    # or for a smaller, quick test model (used as a fallback default in the code if DEFAUT_OLLAMA_MODEL is not set)
    # ollama pull orca-mini
    ```
3.  **Ensure Ollama Service is Running**: Usually starts automatically after install. If not, run `ollama serve`.
4.  **(Optional) Set Environment Variable**: You can specify the default model for the tools by setting the `DEFAULT_OLLAMA_MODEL` environment variable (e.g., `export DEFAULT_OLLAMA_MODEL="deepseek-r1:8b"`). If not set, it defaults to `orca-mini:latest`.

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

**Task Requiring Local LLM (Ollama):**
```bash
# Ensure Ollama is running with a model like 'deepseek-r1:8b' or 'orca-mini'
# export DEFAULT_OLLAMA_MODEL="deepseek-r1:8b" # Optional: to set your preferred model
python run_task.py local_llm_test_summary
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
