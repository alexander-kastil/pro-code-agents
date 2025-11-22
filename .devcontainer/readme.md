# Copilot & Agents Dev Container

## Purpose

This Development Container provides a ready-to-use, reproducible environment for building Microsoft 365 Copilots and AI Agents (declarative agents in Microsoft Copilot Studio, custom engine / pro‑code agents, Microsoft 365 Agents Toolkit solutions, Azure Functions–backed skills, Teams & Adaptive Card extensions, and Graph-integrated workloads). It bundles the core language SDKs, CLIs, local emulators, and VS Code extensions you typically need—so you can focus on solution logic instead of machine setup.

### Key Features

- **🚀 Optimized Performance**: Most tools are pre-installed in the Docker image for faster container startup
- **📓 Jupyter Notebook Support**: Full support for interactive notebooks in Python and C# (.NET Interactive)
- **🔧 Comprehensive Tooling**: Pre-configured with Azure, Microsoft 365, Teams, and Graph development tools
- **✅ Validation Built-in**: Automated setup validation script included

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
- **Microsoft 365 Agents Playground (`@microsoft/m365agentsplayground`)** – Interactive environment for testing agents and skills.
- **Teams CLI (`@microsoft/teams.cli`)** – Command-line interface for Teams app development.
- **Kiota (.NET global tool)** – Generate strongly typed clients from OpenAPI specs for Graph / custom APIs.
- **Dev Tunnels CLI** – Secure tunneling for local development, remote access, and debugging.
- **Jupyter & .NET Interactive** – Full notebook support for Python and C# interactive development and experimentation.

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
- ms-dotnettools.dotnet-interactive-vscode (C# Jupyter notebooks)

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

### 10. Jupyter Notebook Support

The devcontainer includes full support for Jupyter notebooks in both Python and C#:

- **Python Jupyter Kernel**: Pre-installed with `ipykernel` for running Python notebooks
- **.NET Interactive**: Installed for running C# notebooks (polyglot notebooks)
- **VS Code Extensions**: Jupyter extensions for notebook authoring, debugging, and rendering

To use:

- Create a new `.ipynb` file
- Select the appropriate kernel (Python 3 or .NET Interactive)
- Start coding in your preferred language

### 11. Post-Creation Actions

Executed by `post-create.sh` (optimized for speed):

1. Normalize workspace permissions
2. Configure PATH for npm and .NET global tools
3. Install Dev Tunnels CLI (user-specific, optional)
4. Display installed tool versions

**Note**: Most installations (PowerShell, npm packages, .NET tools, Jupyter kernels) are now pre-installed in the Dockerfile for faster container startup.

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

## Using Jupyter Notebooks

The devcontainer includes full support for Jupyter notebooks in both Python and C#.

### Testing the Setup

Sample test notebooks are provided:

- `.devcontainer/test-python-notebook.ipynb` - Tests Python kernel functionality
- `.devcontainer/test-csharp-notebook.ipynb` - Tests C# (.NET Interactive) kernel functionality

### Creating New Notebooks

1. Create a new file with `.ipynb` extension
2. When prompted, select a kernel:
   - **Python 3** - for Python notebooks
   - **.NET (C#)** - for C# notebooks (polyglot notebooks)
3. Start writing code cells

### Features Available

**Python Notebooks:**

- Full Python 3.11 support
- Access to pip-installed packages
- Standard library access
- IPython features

**C# Notebooks:**

- Full C# language support (latest version with .NET 9)
- Async/await support
- LINQ, records, pattern matching
- Access to NuGet packages via `#r "nuget: PackageName"`
- Multi-language support (can mix C#, F#, PowerShell, SQL, etc.)

---

## Validation & Diagnostics

### Quick Validation

Run the automated validation script to check all installations:

```bash
bash .devcontainer/validate-setup.sh
```

This script checks all core tools, Jupyter kernels, PowerShell modules, and optional components.

### Manual Verification

Alternatively, run these commands inside the container to confirm key tooling:

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
npm list -g --depth=0 | grep m365agentsplayground || echo 'M365 Agents Playground missing'
npm list -g --depth=0 | grep teams.cli || echo 'Teams CLI missing'
devtunnel --version || echo 'Dev Tunnels CLI not installed (optional)'
```

### Verify Jupyter Support

```bash
# Check Jupyter installation
jupyter --version

# List available Jupyter kernels
jupyter kernelspec list

# Verify .NET Interactive
dotnet tool list -g | grep dotnet-interactive || echo '.NET Interactive missing'
```

You should see both `python3` and `.net-csharp` kernels listed.

---

Happy building intelligent experiences for Microsoft 365!

---

## Prebuilt Devcontainer Image (Performance Optimization)

To reduce Codespaces / local rebuild time, this repo now publishes a prebuilt devcontainer image to GitHub Container Registry (GHCR).

### Image Coordinates

```
ghcr.io/alexander-kastil/pro-code-agents-dev:latest
```

Additional tags are published per commit SHA and git tags.

### GitHub Action

Workflow: `.github/workflows/devcontainer-image.yml` automatically builds & pushes on changes to `.devcontainer/**`.

### Using the Prebuilt Image (Default)

The default `.devcontainer/devcontainer.json` now references the prebuilt image with the same tooling baked in. Simply open in Codespaces or "Reopen in Container" locally—no build step required beyond pulling the image.

### Switching to Source Build

If you need to modify the Dockerfile:

1. Rename (or move) current `devcontainer.json` to `devcontainer-image.json` (optional backup).
2. Copy `devcontainer-source.json` to `devcontainer.json` (or just rename it):
   ```bash
   mv .devcontainer/devcontainer.json .devcontainer/devcontainer-image.json
   cp .devcontainer/devcontainer-source.json .devcontainer/devcontainer.json
   ```
3. Rebuild:
   ```bash
   # VS Code Command Palette: Dev Containers: Rebuild Container
   # OR Codespaces: Full rebuild
   ```
4. Make your Dockerfile changes, commit, and push. The Action will publish a new image tag.
5. Switch back to the prebuilt image by restoring the original `devcontainer.json` (pointing at `image:`) and rebuilding.

### Forcing a Fresh Pull

If the cached image is used and you want the latest:

```bash
docker pull ghcr.io/alexander-kastil/pro-code-agents-dev:latest
# Then reopen in container (VS Code will use updated local cache).
```

### Pinning a Specific Version

Replace `latest` with a commit tag (e.g., `image": "ghcr.io/alexander-kastil/pro-code-agents-dev:3a1f2c7"`) for reproducible classrooms or workshops.

### Troubleshooting

- If the image fails to pull: ensure `packages: write` permissions exist and the repo visibility allows GHCR access.
- If extensions differ: the image may be outdated—trigger a manual workflow dispatch.
- Permission issues after switching: run `bash .devcontainer/post-create.sh` manually.

---

## Manual Local Build & Push (Optional)

```bash
# Build
docker build -t ghcr.io/alexander-kastil/pro-code-agents-dev:local -f .devcontainer/Dockerfile .

# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u alexander-kastil --password-stdin

# Tag & push
docker tag ghcr.io/alexander-kastil/pro-code-agents-dev:local ghcr.io/alexander-kastil/pro-code-agents-dev:latest
docker push ghcr.io/alexander-kastil/pro-code-agents-dev:latest
```

Use this only when testing changes before committing the workflow adjustments.
