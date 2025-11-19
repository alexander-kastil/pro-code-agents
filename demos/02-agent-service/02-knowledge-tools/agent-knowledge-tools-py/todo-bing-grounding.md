# TODO: agents-bing-grounding.py

## Issue

Missing Bing Search connection configuration.

**Error Message:**

```
ValueError: No value for given attribute
```

## Required Actions

### 1. Create Bing Connection in Azure AI Foundry

1. Go to your Azure AI Foundry project
2. Navigate to "Connections" or "Connected resources"
3. Create a new Bing Search connection
4. Note the connection name

### 2. Update Environment Variable

Update the `BING_CONNECTION` in your `.env` file with the actual connection name:

```
BING_CONNECTION="your-actual-bing-connection-name"
```

### 3. Update Model Deployment (if needed)

The agent may also require a compatible model. Update if necessary:

```
MODEL_DEPLOYMENT="gpt-4o"
```

## Test Command

```bash
python agents-bing-grounding.py
```

## Expected Behavior

The agent should:

1. Connect to Bing Search using the configured connection
2. Create an agent with Bing grounding capabilities
3. Search for "How does wikipedia explain Euler's Identity?"
4. Return an answer with citations from web sources
