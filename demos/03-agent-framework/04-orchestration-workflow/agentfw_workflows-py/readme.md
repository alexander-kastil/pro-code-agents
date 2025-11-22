# Agent Framework Workflows

| Name | Description |
|------|-------------|
| `agentfw_sequential_workflow.py` | Demonstrates a 5-step sequential workflow for invoice processing: (1) loads configuration with tax rates and discounts, (2) reads invoices from CSV and allows user selection, (3) calculates invoice totals with applicable discounts, (4) renders formatted invoice text, and (5) saves the invoice to disk. **Note:** Contains `wait_for_user()` method that pauses between steps, preventing autonomous execution and requiring manual ENTER key presses to proceed. |
