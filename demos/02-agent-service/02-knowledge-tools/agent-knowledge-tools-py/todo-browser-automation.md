# TODO: agents-browser-automation.py

## Issue

Browser Automation features are not available in the current SDK version.

**Error Message:**

```
ImportError: cannot import name 'BrowserAutomationTool' from 'azure.ai.agents.models'
```

## Required Actions

### 1. Check SDK Version

Check your current version:

```bash
pip show azure-ai-agents
```

Current version in requirements.txt: `azure-ai-agents>=1.2.0b2`

### 2. Upgrade SDK (When Available)

Browser Automation may be available in a newer preview version:

```bash
pip install --upgrade azure-ai-agents
```

Or install a specific version that includes this feature (check Azure documentation):

```bash
pip install azure-ai-agents==1.3.0b1  # example - check actual version
```

### 3. Configure Playwright Connection

Once the SDK is upgraded, set the connection ID in `.env`:

```
AZURE_PLAYWRIGHT_CONNECTION_ID="your-playwright-connection-id"
```

You'll need to create a Playwright/Browser Automation connection in Azure AI Foundry.

### 4. Verify Prerequisites

- Ensure your Azure AI Foundry project supports Browser Automation
- This feature may require specific subscription or region

## Test Command

```bash
python agents-browser-automation.py
```

## Expected Behavior

The agent should:

1. Connect to the browser automation service
2. Navigate to finance.yahoo.com
3. Search for "MSFT" (Microsoft stock)
4. Click on "YTD" in the stock chart
5. Extract and report the year-to-date percent change

## Notes

- This feature is likely in preview and may require special access
- Check Azure AI Foundry documentation for Browser Automation availability
- The agent includes a complex multi-step browser interaction example
