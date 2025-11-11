"""
Demo script to showcase the improved HTTP visualization capabilities.

This script simulates a typical agent triage workflow and generates
all three levels of Mermaid diagrams without requiring Azure credentials.
"""
import os
import logging
import sys
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from mermaid_logger import MermaidLogger
from logging_config import HttpLogHandler

def simulate_azure_http_logs(http_logger):
    """Simulate Azure SDK HTTP logs for a complete agent triage workflow."""
    
    # Agent creation sequence
    print("Simulating agent creation...")
    http_logger.info("Request method: 'POST'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/assistants?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 201")
    
    http_logger.info("Request method: 'POST'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/assistants?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 201")
    
    http_logger.info("Request method: 'POST'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/assistants?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 201")
    
    http_logger.info("Request method: 'POST'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/assistants?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 201")
    
    # Thread creation
    print("Simulating thread creation...")
    http_logger.info("Request method: 'POST'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/threads?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 200")
    
    # Message creation
    print("Simulating message creation...")
    http_logger.info("Request method: 'POST'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/threads/thread_abc123def456/messages?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 200")
    
    # Run creation and polling
    print("Simulating run creation and status checks...")
    http_logger.info("Request method: 'POST'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/threads/thread_abc123def456/runs?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 200")
    
    # Poll run status
    http_logger.info("Request method: 'GET'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/threads/thread_abc123def456/runs/run_xyz789012345?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 200")
    
    # List messages
    print("Simulating message retrieval...")
    http_logger.info("Request method: 'GET'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/threads/thread_abc123def456/messages?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 200")
    
    # Cleanup - delete agents
    print("Simulating agent cleanup...")
    http_logger.info("Request method: 'DELETE'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/assistants/asst_priority_agent_123?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 204")
    
    http_logger.info("Request method: 'DELETE'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/assistants/asst_team_agent_456?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 204")
    
    http_logger.info("Request method: 'DELETE'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/assistants/asst_effort_agent_789?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 204")
    
    http_logger.info("Request method: 'DELETE'")
    http_logger.info("Request URL: 'https://eastus.api.azureml.ms/api/projects/pro-code-agents/assistants/asst_triage_agent_000?api-version=2024-07-01-preview'")
    http_logger.info("Response status: 204")


def main():
    """Main demo function."""
    print("=" * 80)
    print("HTTP Call Visualization Demo")
    print("=" * 80)
    print()
    
    # Create mermaid logger with all features enabled
    mermaid_logger = MermaidLogger(enabled=True, verbose=True, http_log=True)
    
    # Set a user prompt for context
    mermaid_logger.log_message_sent(
        'User', 
        'triage-agent', 
        'user_prompt', 
        "Users can't reset their password from the mobile app."
    )
    
    # Create HTTP handler
    http_handler = HttpLogHandler(mermaid_logger)
    http_handler.setLevel(logging.INFO)
    
    # Create and configure HTTP logger
    http_logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
    http_logger.setLevel(logging.INFO)
    http_logger.handlers.clear()
    http_logger.addHandler(http_handler)
    
    # Simulate the HTTP logs
    simulate_azure_http_logs(http_logger)
    
    print()
    print("=" * 80)
    print("Generated HTTP Diagram")
    print("=" * 80)
    print()
    
    # Generate and display the HTTP diagram
    http_diagram = mermaid_logger.get_mermaid_diagram(log_level='http')
    print(http_diagram)
    
    print()
    print("=" * 80)
    print("HTTP Events Summary")
    print("=" * 80)
    print()
    
    # Display HTTP events
    print(f"Total HTTP requests captured: {len(mermaid_logger._http_events)}")
    print()
    print("Detailed event list:")
    for i, event in enumerate(mermaid_logger._http_events, 1):
        request = event.get('request', 'N/A')
        status = event.get('status', 'N/A')
        endpoint = event.get('endpoint', 'N/A')
        print(f"  {i:2d}. {request:35s} -> {status:3s} (endpoint: {endpoint})")
    
    # Save the diagram to a file
    output_dir = 'demo_diagrams'
    os.makedirs(output_dir, exist_ok=True)
    
    print()
    print("=" * 80)
    print("Saving Complete Diagram")
    print("=" * 80)
    print()
    
    mermaid_logger.log_message_sent(
        'triage-agent',
        'User',
        'result',
        'Priority: High, Team: Frontend, Effort: Medium'
    )
    
    mermaid_logger.save_diagram(output_dir=output_dir)
    
    # Find the saved file
    files = [f for f in os.listdir(output_dir) if f.startswith('TICKET-')]
    if files:
        latest_file = sorted(files)[-1]
        filepath = os.path.join(output_dir, latest_file)
        print(f"✓ Diagram saved to: {filepath}")
        print()
        print("You can view this file to see:")
        print("  • Default level: Agent interaction sequence diagram")
        print("  • Verbose level: System setup flowchart")
        print("  • HTTP level: Detailed API communication timeline")
        print()
        print("To visualize the diagrams, open the file in:")
        print("  • VS Code with Markdown Preview Enhanced extension")
        print("  • GitHub (will render Mermaid diagrams automatically)")
        print("  • Any Mermaid-compatible Markdown viewer")
    
    print()
    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
