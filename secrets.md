# Secrets Management Report

## Overview

This report documents the process of securing sensitive information in the demos directory. All .env and appsettings.json files have been scanned, sanitized sample files created, and originals excluded from Git commits.

## Files Scanned

### .env Files

The following .env files were found and processed:

- demos/01-essentials/01-foundry/02-sdks/foundry-sdk-py/.env
- demos/01-essentials/02-agentic-ai/01-prompt-engineering/.env
- demos/01-essentials/02-agentic-ai/02-rag/rag-azure-py/.env
- demos/02-agent-service/01-agent-basics/agent-basics-py/.env
- demos/02-agent-service/02-knowledge-tools/agent-knowledge-tools-py/.env
- demos/02-agent-service/03-connected-agents/connected-agents-py/.env
- demos/03-agent-framework/01-intro/agentfw-agent-py/.env
- demos/03-agent-framework/02-basics/agentfw_basics-py/.env
- demos/03-agent-framework/03-tools-knowledges/agentfw_tools-knowledge-py/.env
- demos/03-agent-framework/04-orchestration-workflow/agentfw_workflows-py/.env

### appsettings.json Files

The following appsettings.json files were found and processed:

- demos/01-essentials/01-foundry/02-sdks/extensions-ai/appsettings.json
- demos/01-essentials/01-foundry/02-sdks/foundry-sdk-cs/appsettings.json
- demos/01-essentials/02-agentic-ai/02-rag/rag-azure-cs/appsettings.json
- demos/01-essentials/02-agentic-ai/03-evaluations/evaluations-cs/appsettings.json
- demos/01-essentials/03-mcp/hr-mcp-server-cs/appsettings.json
- demos/02-agent-service/01-agent-basics/agent-basics/appsettings.json
- demos/02-agent-service/02-knowledge-tools/agent-knowledge-tools/appsettings.json
- demos/02-agent-service/03-connected-agents/connected-agents/appsettings.json
- demos/03-agent-framework/01-intro/agentfw-azure-agent/appsettings.json
- demos/03-agent-framework/02-basics/agentfw_basics/appsettings.json
- demos/03-agent-framework/03-tools-knowledges/agentfw-tools-knowledge/appsettings.json
- demos/03-agent-framework/04-orchestration-workflow/agentfw_workflows/appsettings.json
- demos/03-agent-framework/04-orchestration-workflow/agentfw-orchestration/appsettings.json
- demos/04-copilot-extensibility/02-connectors-api/02-connectors/dotnet/parts-inventory/appsettings.json
- demos/05-integration/01-copilot-studio/copilot-studio-client/appsettings.json
- demos/05-integration/02-foundry-agent/hr-agent-vs/appsettings.json
- demos/05-integration/02-foundry-agent/weather-agent-vs-sk/appsettings.json

## Actions Taken

### Sample Files Created

For each appsettings.json file, a corresponding `appsettings.json.copy` was created with:

- Exact same structure and properties in the same order and formatting
- Sensitive values replaced with "REPLACE_WITH_YOUR_VALUE"

For each .env file, a corresponding `.env.copy` was created with:

- Exact same structure and keys in the same order
- Sensitive values replaced with "REPLACE_WITH_YOUR_VALUE"

### Git Exclusion

- `.env` files are already excluded via `.gitignore`
- Added `demos/**/appsettings.json` to `.gitignore`
- This ensures original files with secrets are not committed to the repository
- Sample files are committed and serve as templates for users

### Sensitive Keys Criteria

Values were replaced for keys containing the following keywords (case-insensitive):

- key
- secret
- connection
- endpoint
- account
- token
- password

## Usage Instructions

1. Copy `appsettings.json.copy` to `appsettings.json` in each demo directory
2. Copy `.env.copy` to `.env` in each demo directory
3. Replace "REPLACE_WITH_YOUR_VALUE" placeholders with your actual configuration values
4. The original `appsettings.json` and `.env` files contain working configurations but are excluded from commits for security

## Security Notes

- Original files with secrets remain in the local workspace but are not tracked by Git
- Sample files provide the structure without exposing sensitive data
- Users can safely clone the repository and configure their own secrets
