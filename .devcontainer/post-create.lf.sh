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

# Install PowerShell (pwsh) when it's not already present
if ! command -v pwsh >/dev/null 2>&1; then
  echo "Installing PowerShell Core (pwsh)..."
  sudo apt-get update
  sudo apt-get install -y wget apt-transport-https software-properties-common gpg
  wget -q https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb
  sudo dpkg -i /tmp/packages-microsoft-prod.deb
  rm -f /tmp/packages-microsoft-prod.deb
  sudo apt-get update
  sudo apt-get install -y powershell
else
  echo "PowerShell Core already installed. Skipping installation."
fi

# Install required PowerShell modules using pwsh
echo "Installing required PowerShell modules..."
pwsh -NoLogo -NoProfile -Command "\
  Set-PSRepository -Name PSGallery -InstallationPolicy Trusted; \
  Install-Module -Name Microsoft.Graph -Scope CurrentUser -Force -AcceptLicense -ErrorAction Stop; \
  Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser -Force -ErrorAction Stop; \
  Write-Host 'PowerShell modules installed successfully.'"

# Fix npm global permissions and install Microsoft 365 Agents Toolkit CLI
if ! npm list -g @microsoft/m365agentstoolkit-cli >/dev/null 2>&1; then
  echo "Installing Microsoft 365 Agents Toolkit CLI..."
  # Fix npm permissions for global installs
  sudo chown -R "${TARGET_USER}:${TARGET_GROUP}" /usr/local/lib/nodejs/
  sudo chmod -R u+rwX,go+rX /usr/local/lib/nodejs/
  npm install -g @microsoft/m365agentstoolkit-cli
else
  echo "Microsoft 365 Agents Toolkit CLI already installed."
fi

# Install Teams CLI
if ! npm list -g @microsoft/teams.cli >/dev/null 2>&1; then
  echo "Installing Teams CLI..."
  npm install -g @microsoft/teams.cli
else
  echo "Teams CLI already installed."
fi

# Install Microsoft Agents Playground
if ! npm list -g @microsoft/m365agentsplayground >/dev/null 2>&1; then
  echo "Installing Microsoft Agents Playground..."
  npm install -g @microsoft/m365agentsplayground
else
  echo "Microsoft Agents Playground already installed."
fi

# Install Kiota as a global .NET tool
if ! dotnet tool list -g | grep -q "Microsoft.OpenApi.Kiota"; then
  echo "Installing Kiota global .NET tool..."
  dotnet tool install --global Microsoft.OpenApi.Kiota
else
  echo "Kiota global .NET tool already installed."
fi

# Install Dev Tunnels CLI
if ! command -v devtunnel >/dev/null 2>&1; then
  echo "=== Installing Dev Tunnels CLI ==="
  curl -sL https://aka.ms/DevTunnelCliInstall | bash
  # Add ~/bin to PATH for current session
  export PATH="$HOME/bin:$PATH"
  echo "Dev Tunnels CLI installed successfully"
else
  echo "Dev Tunnels CLI already installed."
fi
