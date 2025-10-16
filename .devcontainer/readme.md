# Copilot & Agents Dev Container

## Purpose

This Development Container provides a ready-to-use, reproducible environment for building Microsoft 365 Copilots and AI Agents (declarative agents in Microsoft Copilot Studio, custom engine / pro‑code agents, Microsoft 365 Agents Toolkit solutions, Azure Functions–backed skills, Teams & Adaptive Card extensions, and Graph-integrated workloads). It bundles the core language SDKs, CLIs, local emulators, and VS Code extensions you typically need—so you can focus on solution logic instead of machine setup.

---

## Getting Started

### 1.1 Fork the Repository

Before you start, please fork this repository to your GitHub account by clicking the `Fork` button in the upper right corner of the repository's main screen (or follow the [documentation](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo#forking-a-repository)). This will allow you to make changes to the repository and save your progress.

### 1.2 Spin up Development Environment

GitHub Codespaces is a cloud-based development environment that allows you to code from anywhere. It provides a fully configured environment that can be launched directly from any GitHub repository, saving you from lengthy setup times. You can access Codespaces from your browser, Visual Studio Code, or the GitHub CLI, making it easy to work from virtually any device.

To open GitHub Codespaces, click on the button below:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/)

> Note: You can also use this dev container locally with VS Code and Docker. Read [Develop inside a Container](https://code.visualstudio.com/docs/devcontainers/containers) for instructions.

## Inventory (What’s Inside & Why)

### 1. Language SDKs & Runtimes

- **.NET 9.0 SDK** (base image + devcontainer feature) – For C# agents, Azure Functions (in-process / isolated), Kiota-generated clients, and Graph integrations.
- **Node.js 24.x** (installed twice: via Dockerfile and the devcontainer feature) – For TypeScript/JavaScript agent tooling, Azure Functions (Node runtime), Playwright tests, M365 Agents Toolkit CLI, build pipelines.
  - Note: The duplication is harmless but redundant; you can remove one source in future optimization.
- **Python 3.11** – For Python-based experimentation, data enrichment steps, or prototyping AI components.
- **PowerShell Core (pwsh)** – For Microsoft 365 administrative scripting, Graph & SharePoint module usage.

### 2. Core Cloud & Development CLIs

- **Azure CLI (az)** – Manage Azure resources, deploy Functions, configure identities.
- **Azure Developer CLI (azd)** – Opinionated infra + app provisioning & deployment flows for Azure-based agent backends.
- **GitHub CLI (gh)** – Repository operations, workflow inspection, auth, Codespaces initiation.
- **Git** – Source control (provided via feature and base image).

### 3. Serverless & Local Emulation

- **Azure Functions Core Tools v4 (func)** – Create, run, debug, and publish Azure Functions used as skills/actions.
- **Azurite** – Local Azure Storage emulator (Queues/Blob/Tables) for Functions bindings or state storage.

### 4. Agent & API Productivity Tooling

- **Microsoft 365 Agents Toolkit CLI (`@microsoft/m365agentstoolkit-cli`)** – Scaffolding & managing M365 agent solutions.
- **Microsoft 365 Agents Playground (`@microsoft/m365agentstoolkit-playground`)** – Interactive environment for testing agents and skills.
- **Kiota (.NET global tool)** – Generate strongly typed clients from OpenAPI specs for Graph / custom APIs.
- **Dev Tunnels CLI (`Microsoft.DevTunnels.Cli`)** – Secure tunneling for local development, remote access, and debugging.

### 5. PowerShell Modules (Installed for Current User)

- **Microsoft.Graph** – Unified Graph API module for automation.
- **Microsoft.Online.SharePoint.PowerShell** – SharePoint Online admin & provisioning scripts.

### 6. Supporting Utilities

- **curl, wget, ca-certificates, gnupg, apt-transport-https** – Added during CLI installations.
- **Timezone set to UTC** – Ensures consistent logs & reproducibility.

### 7. Forwarded / Common Ports

- **4200** – Commonly used by local web UIs (e.g., Angular or custom dashboards).
- **5000, 5001** – Default ASP.NET Kestrel HTTP/HTTPS development ports.

### 8. VS Code Extensions (Curated)

Grouped by purpose:

#### .NET / C#

- ms-dotnettools.csharp
- ms-dotnettools.csdevkit
- ms-dotnettools.vscode-dotnet-runtime
- ms-dotnettools.vscodeintellicode-csharp
- aliasadidev.nugetpackagemanagergui

#### Azure & Cloud

- ms-azuretools.vscode-azurefunctions
- ms-azuretools.vscode-azurecontainerapps
- ms-azuretools.vscode-bicep
- ms-azuretools.vscode-docker
- ms-vscode.azurecli

#### AI, Copilot & Agents

- github.copilot
- github.copilot-chat
- ms-copilotstudio.vscode-copilotstudio (Copilot Studio authoring)
- teamsdevapp.vscode-ai-foundry (Azure AI / AI Foundry integration)
- ms-windows-ai-studio.windows-ai-studio

#### Microsoft 365 / Teams / Graph

- teamsdevapp.ms-teams-vscode-extension (Teams apps / extensions)
- TeamsDevApp.vscode-adaptive-cards (Adaptive Cards tooling)
- ms-graph.kiota (Graph client generation integration)

#### Python & Data / Jupyter

- ms-python.python
- ms-python.vscode-pylance
- ms-python.vscode-python-envs
- ms-python.debugpy
- ms-toolsai.jupyter (+ keymap, renderers, cell-tags, slideshow)

#### Web / Testing / Tooling

- esbenp.prettier-vscode (formatting)
- ms-playwright.playwright (browser automation/tests)
- docker.docker (container management)
- humao.rest-client (API testing)

#### Authoring & Quality

- mdickin.markdown-shortcuts
- streetsidesoftware.code-spell-checker
- kevinrose.vsc-python-indent

### 9. Dev Container Features (Declarative)

- node:24.0.0
- dotnet:9.0
- git:latest
- python:3.11

### 10. Post-Creation Actions

Executed by `post-create.sh`:

1. Normalize workspace permissions.
2. Install PowerShell Core (if missing).
3. Install Graph + SharePoint PS modules.
4. Install Microsoft 365 Agents Toolkit CLI (global npm).
5. Install Kiota (.NET global tool).

---

## Quick Start (Local VS Code)

### Prerequisites

- Docker (latest Desktop or engine) running.
- VS Code with the Dev Containers extension (ms-vscode-remote.remote-containers) OR the built-in Dev Containers support.
- (Optional) GitHub & Azure CLI auth tokens/identities ready.

### Steps

1. Clone the repo:
   ```bash
   git clone https://github.com/arambazamba/m365-copilot-dev.git
   cd m365-copilot-dev
   ```
2. Open the folder in VS Code.
3. When prompted, choose: “Reopen in Container” (or use Command Palette → Dev Containers: Reopen in Container).
4. Wait for build (image + Dockerfile layers) and post-create script to finish.
5. Open a terminal inside the container and validate installations (see Validation section).

### Rebuilding / Updating

Use “Dev Containers: Rebuild Container” if you change the Dockerfile, features, or post-create script.

---

## Quick Start (GitHub Codespaces)

1. Navigate to the repository in GitHub.
2. Click the green “Code” button → “Create codespace on master”.
3. Codespaces uses the same `devcontainer.json`; build + provisioning runs automatically.
4. After startup, open a terminal and perform validation checks.

### Persisting Customizations

Add changes to `.devcontainer/*` and commit. Codespaces + local rebuilds will pick them up automatically.

---

## Validation & Diagnostics

Run these inside the container to confirm key tooling:

```bash
dotnet --info | grep 'Version:' | head -n 1
node -v
npm -v
python --version
pwsh --version
az version | head -n 3
azd version
gh --version | head -n 1
func --version
azurite --version
dotnet tool list -g | grep Kiota || echo 'Kiota missing'
npm list -g --depth=0 | grep m365agentstoolkit || echo 'M365 Agents Toolkit CLI missing'
dotnet tool list -g | grep DevTunnels || echo 'Dev Tunnels CLI missing'
agentsplayground --version
```

Happy building intelligent experiences for Microsoft 365!
