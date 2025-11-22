# Agent Framework Workflows

## Overview

This collection demonstrates various workflow orchestration patterns using the Agent Framework for invoice processing scenarios. All samples share common functionality through `utils/invoice_utils.py`, which provides:

- **Invoice data model** (`InvoiceData`) with CSV loading
- **Configuration management** (`InvoiceConfig`) for tax rates, discounts, and thresholds
- **Calculation utilities** for subtotals, discounts (high-value and preferred client), and taxes
- **Rendering and I/O** for formatting invoices and saving to `output/invoices/`
- **Logging and archiving** with structured output to `output/logs/` and `output/archive/`

Each workflow demonstrates different orchestration patterns while processing the same invoice data, allowing for direct comparison of approaches.

## Workflow Samples

| Name | Description |
|------|-------------|
| `agentfw_sequential_workflow.py` | Linear 5-step workflow: configuration → invoice selection → calculation → rendering → saving. **Contains `wait_for_user()` pauses between steps, requiring manual ENTER presses.** |
| `agentfw_concurrent_workflow.py` | Demonstrates parallel processing with fan-out/fan-in pattern. Dispatcher splits work into 3 concurrent tasks (totals calculator, client preparer, credit checker) that execute simultaneously, then merges results for final rendering. Shows independent task parallelism. |
| `agentfw_branching_workflow.py` | Conditional routing workflow with multiple decision points: checks for existing files to archive, applies discounts based on invoice value and client status (high-value/preferred/standard branches), demonstrates data-driven path selection. |
| `agentfw_visualization_workflow.py` | Interactive workflow pattern visualizer. Generates Mermaid diagrams (`.mmd` files) for sequential, parallel, and branching patterns. Outputs to `output/visualizations/` for documentation and presentations. |
| `agentfw_interactive_checkpointing.py` | Human-in-the-loop workflow with automatic state persistence. Pauses for user confirmation on tax rates and discounts, saves checkpoints at each pause point, supports resume from interruption with full state restoration. |
| `agentfw_agents_in_workflow.py` | AI agents integrated into workflow steps. Uses Azure AI agents for intelligent processing: analyzes invoices, makes business decisions, generates personalized communications, and creates executive summaries. Requires Azure AI Project configuration. |
