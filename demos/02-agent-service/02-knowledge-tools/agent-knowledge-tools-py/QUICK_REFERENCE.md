# Agent Testing Quick Reference

## ✅ Fully Working (3 agents)

- `agents-file-search.py` - Basic agent with conversation
- `agents-code-interpreter.py` - Data analysis with file upload
- `agents-function-calling.py` - Custom function calls (interactive)

## ⚠️ Need Configuration (5 agents)

| Agent                      | Main Issue                                  | Todo File                |
| -------------------------- | ------------------------------------------- | ------------------------ |
| `agents-ai-search-rag.py`  | Model compatibility + Azure AI Search setup | `todo-ai-search-rag.md`  |
| `agents-bing-grounding.py` | Missing Bing connection                     | `todo-bing-grounding.md` |
| `agents-sharepoint.py`     | Missing SharePoint connection               | `todo-sharepoint.md`     |
| `agents-mcp.py`            | Model compatibility                         | `todo-mcp.md`            |
| `agents-azfunction.py`     | Azure Function deployment needed            | `todo-azfunction.md`     |

## ❌ SDK Not Available (2 agents)

| Agent                          | Issue                               | Todo File                    |
| ------------------------------ | ----------------------------------- | ---------------------------- |
| `agents-browser-automation.py` | SDK version doesn't include feature | `todo-browser-automation.md` |
| `agents-computer-use.py`       | SDK version doesn't include feature | `todo-computer-use.md`       |

## Quick Fixes

### Priority 1: Model Upgrade

Update in `.env`:

```bash
MODEL_DEPLOYMENT="gpt-4o"
```

This will fix: `agents-ai-search-rag.py`, `agents-mcp.py`

### Priority 2: Create Connections in Azure AI Foundry

1. Bing Search connection → Update `BING_CONNECTION`
2. SharePoint connection → Update `SHAREPOINT_CONNECTION`
3. Azure AI Search index → Create `insurance-documents-index`

### Priority 3: Deploy Azure Function

- Deploy currency converter function
- Update `FUNCTION_DEPLOYMENT_URL` in `.env`

## Files Created/Modified

✅ `function_calling_functions.py` - Support module for function calling
✅ `.env.copy` - Updated with all required variables
✅ `agents-mcp.py` - Fixed import error
✅ `todo.md` - Main testing summary
✅ 7 individual todo files for problematic agents

## Test Commands

```bash
# Working agents
python agents-file-search.py
python agents-code-interpreter.py
python agents-function-calling.py  # interactive

# After configuration
python agents-ai-search-rag.py
python agents-bing-grounding.py
python agents-sharepoint.py
python agents-mcp.py
python agents-azfunction.py  # interactive

# After SDK upgrade
python agents-browser-automation.py
python agents-computer-use.py
```
