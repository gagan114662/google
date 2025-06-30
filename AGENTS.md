# AGENTS.md - Project Chimera Core API

This document provides guidelines and instructions for AI agents (and human developers) working on the Project Chimera Core API codebase.

## Overview

Project Chimera aims to be an open-source platform for autonomous AI agents. This specific component is the backend Core API, built with FastAPI, and also includes a local task runner for development and testing of agent capabilities.

Refer to the `Product Requirements Document (PRD) Project Chimera.md` for the full project vision, architecture, and requirements.

## Project Structure Overview

*   **`app/`**: Houses the FastAPI backend application code.
    *   **`app/tools/`**: Contains low-level, reusable "tools" for agents.
        *   `web_scraper.py`: Includes static (`requests`) and dynamic (`Botasaurus`) content fetching, experimental dynamic Google search, and screenshot capabilities.
        *   `file_system.py`: For local file operations within the `workspace/`.
        *   `content_generator.py`: For creating text files, PDFs, Excel sheets. **Now integrates with local LLMs via Ollama for summarization and email drafting.**
    *   **`app/skills/`**: Contains higher-level "skills" that compose tools.
        *   `web_research.py`: Skills for static/dynamic URL text extraction and static/dynamic web search.
        *   `reporting.py`: Skills for creating reports.
    *   **`app/llm/`**: Client for interacting with local LLMs.
        *   `ollama_client.py`: Client for Ollama service.
    *   Other directories (`api/`, `core/`, `models/`, `services/`) are primarily for the FastAPI backend.
*   **`run_task.py`**: A command-line script for executing local agent tasks. This is the primary way to test tool and skill functionality without needing the full API and UI.
*   **`workspace/`**: A directory automatically created (and cleaned) by `run_task.py` for file inputs/outputs during local task execution.
*   **`AGENTS.md`**: This file.
*   **`README.md`**: General project overview and setup for the local task runner.
*   **`requirements.txt`**: Python dependencies for both the API and the local runner.

## Development Setup

### 1. Environment
*   Ensure you have Python 3.11+ installed.
*   It's highly recommended to use a virtual environment (e.g., `venv` or `conda`):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

### 2. Dependencies
*   Install dependencies from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Running Local Agent Tasks (using `run_task.py`)
This is the recommended way to test and develop individual tools and skills.
*   The `run_task.py` script provides a CLI to execute predefined local tasks.
*   It sets up a `workspace/` directory for file operations.
*   **Usage**:
    ```bash
    python run_task.py <task_name>
    ```
*   **Available tasks** (see `run_task.py` or `README.md` for the current list, e.g.):
    *   `example`: A very simple task to show orchestration.
    *   `excel_lotto`: Generates an Excel file with lottery data in `workspace/`.
    *   `dynamic_scrape_test`: Tests dynamic web scraping. **Requires `xvfb-run`** (e.g., `xvfb-run -a python run_task.py dynamic_scrape_test`).
    *   `local_llm_test_summary`: Tests local LLM text summarization. **Requires Ollama service and a model.**
*   You can add new tasks to `run_task.py` to test different tool/skill combinations.
*   **Note on Xvfb:** Tasks using dynamic browser automation (Botasaurus) require a virtual display environment like Xvfb when running in headless server environments. Ensure Xvfb is installed (`sudo apt-get install xvfb`) and prefix your command with `xvfb-run -a`.
*   **Note on Ollama for Local LLM:**
    *   To use tools that leverage local LLMs (e.g., `generate_summary_local_llm`), you need to have Ollama installed and running.
    *   Install Ollama from [https://ollama.com](https://ollama.com). (Linux: `curl -fsSL https://ollama.com/install.sh | sh`)
    *   Pull a model. `deepseek-r1:8b` is recommended for quality, or `deepseek-r1:7b`/`deepseek-r1:1.5b` for lighter versions. For basic testing, `orca-mini` (the code's fallback default if `DEFAULT_OLLAMA_MODEL` env var is not set) can be used:
        ```bash
        ollama pull deepseek-r1:8b
        # or
        ollama pull orca-mini
        ```
    *   Ensure the Ollama service is active (`ollama serve` if not started automatically).
    *   The `DEFAULT_OLLAMA_MODEL` environment variable can be set to specify your preferred default model (e.g., `export DEFAULT_OLLAMA_MODEL="deepseek-r1:8b"`).

### 4. Database & Services (for the full FastAPI API)
*   The full FastAPI backend (`app/main.py`) requires PostgreSQL and Redis instances. These are **not required** for running local tasks with `run_task.py` unless a task specifically tries to initialize these API core components.
*   If you intend to run the FastAPI backend:
    *   Ensure PostgreSQL and Redis are running and accessible.
    *   Copy `.env.example` to `.env` and update `DATABASE_URL` and `REDIS_URL`.
        ```bash
        cp .env.example .env
        # Then edit .env with your actual credentials
        ```

### 5. Running the API (FastAPI backend)
*   The main FastAPI application is in `app/main.py`.
*   To run the development server:
        ```bash
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        ```
    *   You should see output indicating the server is running, typically on `http://localhost:8000`.
    *   Access the health check endpoint at `http://localhost:8000/health`.
    *   Interactive API documentation (Swagger UI) will be available at `http://localhost:8000/docs`.
    *   Alternative API documentation (ReDoc) will be available at `http://localhost:8000/redoc`.

## Coding Conventions

*   **Python:**
    *   Follow PEP 8 guidelines.
    *   Use Black for code formatting and Ruff for linting (configurations to be added).
    *   Use type hints extensively.
*   **Commit Messages:**
    *   Follow Conventional Commits specification (e.g., `feat: add user authentication endpoint`).
*   **Branching:**
    *   Use feature branches (e.g., `feat/user-auth`, `fix/health-check-bug`).
    *   Prefix branch names with `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`, etc.

## Testing

*   (Testing framework and guidelines to be added - likely Pytest)
*   Ensure new features are accompanied by tests.
*   All tests must pass before merging code.

## Agent-Specific Instructions

*   **Understanding the Goal:** Before making changes, ensure you understand the task in the context of the overall PRD. If ambiguous, ask for clarification.
*   **Planning:** Always formulate a plan and get approval if it significantly deviates from the current task or involves major architectural changes.
*   **Modularity:** Strive for modular code. New functionalities, especially agent tools or services, should be designed as reusable components.
*   **Security:** Security is paramount. Be mindful of potential vulnerabilities, especially when dealing with code execution, file system access, or external APIs. Follow the sandboxing principles outlined in the PRD.
*   **Dependencies:** When adding new dependencies:
    1.  Add them to `requirements.txt`.
    2.  Ensure they are compatible with the project's license (Apache 2.0).
    3.  Consider the security implications of adding new packages.
*   **PRD Adherence:** The PRD is the source of truth. Features and architectural decisions should align with it.

This `AGENTS.md` will evolve as the project grows. Always refer to the latest version.
