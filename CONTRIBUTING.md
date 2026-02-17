# Contributing to Repo Health Dashboard

Thank you for your interest in improving the Repo Health Dashboard. This project benefits from a community of contributors who care about safe, respectful, and reliable tooling for AI Village repositories.

## Core Principles
All contributions must uphold the civic-safety-guardrails governance standards and their four pillars:
- **Evidence:** Ground changes in data, observed behavior, or documented requirements. Favor measurable impact over guesswork.
- **Privacy:** Minimize collection and exposure of sensitive data. Default to least privilege and anonymize when possible.
- **Non-Carceral:** Avoid punitive patterns in tooling or language. Promote supportive feedback and constructive remediation paths.
- **Safety:** Reduce harm vectors, prevent misuse, and add safeguards for both maintainers and users when introducing new features.

## How to Contribute
- Create a feature branch from `main` for your work (no forks needed for internal contributors).
- Set up a Python environment (`python -m venv .venv && source .venv/bin/activate`) and install dependencies (e.g., `pip install -r requirements.txt` if present).
- Focus your contributions on Python and scripting improvements: new checks, data collectors, CLI utilities, or automation that strengthens repo health insights.
- Write or update tests for any new script or health rule you add.
- Run the health check locally before submitting to ensure dashboards and reports render correctly.
- Open a pull request with a concise description, rationale, and testing notes.

## Style Guide
- Follow PEP 8 for all Python code; use clear, descriptive variable and function names.
- Prefer small, composable functions with docstrings that explain intent and inputs/outputs.
- Use type hints where practical to make scripts easier to maintain and review.

## Code of Conduct
Please review and adhere to the guidelines in `CODE_OF_CONDUCT.md`. Interactions in issues, discussions, and pull requests are expected to remain respectful and inclusive.
