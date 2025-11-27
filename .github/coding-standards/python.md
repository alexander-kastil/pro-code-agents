# Python Coding Standards

## Quick Reference

- Use `.env` files for configuration
- Type hints for function parameters and returns
- `requirements.txt` AND `pyproject.toml` for dependencies
- Follow PEP 8 guidelines
- Use async/await for Azure SDK operations

## Virtual Environment Management

### Creating Virtual Environments

**CRITICAL**: ALWAYS use terminal commands to create and manage Python virtual environments. NEVER use VS Code extensions or UI-based tools.

#### Windows PowerShell
```powershell
# Create new virtual environment
python -m venv .venv

# Activate the environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### Linux/macOS
```bash
# Create new virtual environment
python -m venv .venv

# Activate the environment
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### Recreating a Corrupted Environment
If the environment becomes corrupted or has package conflicts:

```powershell
# Windows PowerShell
if (Test-Path .venv) { Remove-Item -Recurse -Force .venv }
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

```bash
# Linux/macOS
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Building and Testing

- This repository uses `uv` for Python dependency management
- **IMPORTANT**: Always maintain synchronized `requirements.txt` and `pyproject.toml` files
- Install dependencies: `uv pip install -r requirements.txt` or `uv sync`
- Main dependencies: azure-ai-projects, azure-ai-inference, azure-ai-evaluation, agent-framework
