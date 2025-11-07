#!/usr/bin/env bash

set -euo pipefail

echo "Post-creation setup starting..."

# Fix permissions for the workspace directory
echo "Setting correct permissions for workspace directory..."
TARGET_USER="${SUDO_USER:-${DEVCONTAINER_USER:-${USERNAME:-${USER:-}}}}"
if [[ -z "${TARGET_USER}" ]] || ! id -u "${TARGET_USER}" >/dev/null 2>&1; then
  TARGET_USER="$(awk -F: '$3>=1000 && $1!="nobody" {print $1; exit}' /etc/passwd)"
fi
TARGET_GROUP="$(id -gn "${TARGET_USER}" 2>/dev/null || true)"
if [[ -z "${TARGET_GROUP}" ]]; then
  TARGET_GROUP="${TARGET_USER}"
fi
echo "Ensuring /workspace is owned by ${TARGET_USER}:${TARGET_GROUP}"
sudo chown -R "${TARGET_USER}:${TARGET_GROUP}" /workspace
sudo chmod -R u+rwX,go+rX /workspace

# Navigate to the workspace root
cd /workspace

# Create Python virtual environment at the root if it doesn't exist
if [[ ! -d "/workspace/.venv" ]]; then
  echo "Creating Python virtual environment at /workspace/.venv..."
  python3 -m venv /workspace/.venv
  echo "Python virtual environment created successfully."
fi

# Install requirements from requirements.txt
if [[ -f "/workspace/requirements.txt" ]]; then
  echo "Installing Python packages from requirements.txt..."
  /workspace/.venv/bin/pip install --upgrade pip
  /workspace/.venv/bin/pip install -r /workspace/requirements.txt
  echo "Python packages installed successfully."
else
  echo "Warning: requirements.txt not found, skipping package installation."
fi

# Set proper ownership for the virtual environment
chown -R "${TARGET_USER}:${TARGET_GROUP}" /workspace/.venv

# Ensure npm global bin directory is on PATH for current and future shells
GLOBAL_NPM_PREFIX="$(npm prefix -g 2>/dev/null || true)"
if [[ -n "${GLOBAL_NPM_PREFIX}" ]]; then
  GLOBAL_NPM_BIN="${GLOBAL_NPM_PREFIX}/bin"
  if [[ -d "${GLOBAL_NPM_BIN}" ]]; then
    if ! echo ":${PATH}:" | grep -q ":${GLOBAL_NPM_BIN}:/"; then
      echo "Adding ${GLOBAL_NPM_BIN} to current PATH"
      export PATH="${GLOBAL_NPM_BIN}:${PATH}"
    fi
    if [[ ! -f /etc/profile.d/npm-global-path.sh ]] || ! grep -q "${GLOBAL_NPM_BIN}" /etc/profile.d/npm-global-path.sh 2>/dev/null; then
      echo "Persisting npm global bin path"
      echo "export PATH=\"${GLOBAL_NPM_BIN}:\\$PATH\"" | sudo tee /etc/profile.d/npm-global-path.sh >/dev/null
    fi
  fi
fi

# Ensure .dotnet/tools is on PATH
if [[ -d "$HOME/.dotnet/tools" ]]; then
  if ! echo ":${PATH}:" | grep -q ":$HOME/.dotnet/tools:/"; then
    echo "Adding $HOME/.dotnet/tools to current PATH"
    export PATH="$HOME/.dotnet/tools:${PATH}"
  fi
  if [[ ! -f ~/.bashrc ]] || ! grep -q ".dotnet/tools" ~/.bashrc 2>/dev/null; then
    echo "Persisting .dotnet/tools path to .bashrc"
    echo 'export PATH="$PATH:$HOME/.dotnet/tools"' >> ~/.bashrc
  fi
fi

# Ensure .NET Interactive kernels are registered with Jupyter
if command -v dotnet-interactive >/dev/null 2>&1; then
  echo "Registering .NET Interactive kernels with Jupyter..."
  dotnet interactive jupyter install
else
  echo "dotnet-interactive command not found; skipping Jupyter kernel registration"
fi

# Install Dev Tunnels CLI (optional, user-specific installation)
if ! command -v devtunnel >/dev/null 2>&1; then
  echo "Installing Dev Tunnels CLI..."
  curl -sL https://aka.ms/DevTunnelCliInstall | bash
  export PATH="$HOME/bin:$PATH"
  echo "Dev Tunnels CLI installed successfully"
else
  echo "Dev Tunnels CLI already installed."
fi

echo "Post-creation setup completed successfully!"
echo ""
echo "Available tools:"
echo "  - .NET SDK: $(dotnet --version)"
echo "  - Node.js: $(node --version)"
echo "  - Python: $(python --version)"
echo "  - PowerShell: $(pwsh --version | head -1)"
echo "  - Azure CLI: $(az --version | head -1)"
echo "  - Jupyter: $(jupyter --version | head -1)"
if command -v dotnet-interactive >/dev/null 2>&1; then
    echo "  - .NET Interactive: $(dotnet interactive --version 2>&1 | head -1 || echo 'tool available')"
else
    echo "  - .NET Interactive: not found in PATH"
fi
echo ""
echo "Python virtual environment created at /workspace/.venv"
echo "To activate the virtual environment, run: source /workspace/.venv/bin/activate"
echo "All Python scripts in demos/01-essentials will use this shared environment."
echo ""
echo "Ready for development with Jupyter notebook support for Python and C#!"
