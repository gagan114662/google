# AGENTS.md - Project Chimera Core API

This document provides guidelines and instructions for AI agents (and human developers) working on the Project Chimera Core API codebase.

## Overview

Project Chimera aims to be an open-source platform for autonomous AI agents. This specific component is the backend Core API, built with FastAPI.

Refer to the `Product Requirements Document (PRD) Project Chimera.md` for the full project vision, architecture, and requirements.

## Development Setup

1.  **Environment:**
    *   Ensure you have Python 3.11+ installed.
    *   It's highly recommended to use a virtual environment (e.g., `venv` or `conda`).
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```

2.  **Dependencies:**
    *   Install dependencies from `requirements.txt`:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Database & Services:**
    *   This project requires PostgreSQL and Redis instances.
    *   Ensure they are running and accessible.
    *   Copy `.env.example` to `.env` and update the `DATABASE_URL` and `REDIS_URL` variables with your connection details.
        ```bash
        cp .env.example .env
        # Then edit .env with your actual credentials
        ```

4.  **Running the API:**
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
