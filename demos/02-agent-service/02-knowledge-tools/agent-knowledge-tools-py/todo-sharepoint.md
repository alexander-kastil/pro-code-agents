# TODO: agents-sharepoint.py

## Issue

Missing SharePoint connection configuration.

**Error Message:**

```
ValueError: No value for given attribute
```

## Required Actions

### 1. Create SharePoint Connection in Azure AI Foundry

1. Go to your Azure AI Foundry project
2. Navigate to "Connections" or "Connected resources"
3. Create a new SharePoint connection
4. Configure authentication (OAuth or Service Principal)
5. Note the connection name

### 2. Update Environment Variable

Update the `SHAREPOINT_CONNECTION` in your `.env` file:

```
SHAREPOINT_CONNECTION="your-actual-sharepoint-connection-name"
```

### 3. Update the Query in Code

The agent currently has a placeholder in the message content. Update line ~52 in `agents-sharepoint.py`:

```python
# Current (line ~52):
content="Hello, summarize the key points of the <sharepoint_resource_document>",

# Replace with actual SharePoint document reference:
content="Hello, summarize the key points of the Q1 Sales Report",
```

### 4. Update Model Deployment (if needed)

The agent may require a compatible model:

```
MODEL_DEPLOYMENT="gpt-4o"
```

## Test Command

```bash
python agents-sharepoint.py
```

## Expected Behavior

The agent should:

1. Connect to SharePoint using the configured connection
2. Create an agent with SharePoint access
3. Retrieve and summarize the specified document
4. Return the summary with citations
