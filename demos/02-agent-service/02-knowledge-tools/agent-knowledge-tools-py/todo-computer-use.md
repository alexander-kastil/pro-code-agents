# TODO: agents-computer-use.py

## Issue

Computer Use features are not available in the current SDK version.

**Error Message:**

```
ImportError: cannot import name 'ComputerScreenshot' from 'azure.ai.agents.models'
```

## Required Actions

### 1. Check SDK Version

Check your current version:

```bash
pip show azure-ai-agents
```

Current version in requirements.txt: `azure-ai-agents>=1.2.0b2`

### 2. Upgrade SDK (When Available)

Computer Use may be available in a newer preview version:

```bash
pip install --upgrade azure-ai-agents
```

Or install a specific version that includes this feature (check Azure documentation):

```bash
pip install azure-ai-agents==1.3.0b1  # example - check actual version
```

### 3. Configure Computer Use Environment

Once the SDK is upgraded, set the environment in `.env`:

```
COMPUTER_USE_ENVIRONMENT="your-computer-use-environment-id"
```

You'll need to create a Computer Use environment in Azure AI Foundry.

### 4. Verify Asset Files

The agent expects these asset files to exist:

- `../assets/cua_screenshot.jpg` - Initial screenshot
- `../assets/cua_screenshot_next.jpg` - Result screenshot

Create the `assets` folder at the parent directory level or update the paths in the code.

### 5. Verify Prerequisites

- Ensure your Azure AI Foundry project supports Computer Use
- This feature may require specific subscription or region
- Computer Use is typically an advanced preview feature

## Test Command

```bash
python agents-computer-use.py
```

## Expected Behavior

The agent should:

1. Load a screenshot of a web browser
2. Analyze the screenshot (Bing search page)
3. Simulate typing "movies near me" in the search box
4. Submit tool outputs with the action result
5. Display the agent's response

## Notes

- Computer Use is an advanced AI feature for GUI automation
- This feature is likely in preview and may require special access
- Check Azure AI Foundry documentation for Computer Use availability
- The agent uses a 1026x769 viewport (browser-sized display)
- Requires images to be base64 encoded for transmission
