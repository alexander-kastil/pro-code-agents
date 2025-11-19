# Python Coding Standards

## Quick Reference

- Use `.env` files for configuration
- Type hints for function parameters and returns
- `requirements.txt` AND `pyproject.toml` for dependencies
- Follow PEP 8 guidelines
- Use async/await for Azure SDK operations

## Building and Testing

- This repository uses `uv` for Python dependency management
- **IMPORTANT**: Always maintain synchronized `requirements.txt` and `pyproject.toml` files
- Install dependencies: `uv pip install -r requirements.txt` or `uv sync`
- Main dependencies: azure-ai-projects, azure-ai-inference, azure-ai-evaluation, agent-framework
