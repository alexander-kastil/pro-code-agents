"""
External MCP Server Demo - Weather MCP

This demo shows how to connect to an external MCP (Model Context Protocol) server.
We'll connect to a hypothetical weather MCP server that provides weather information.

MCP servers can be:
- Local servers running via uvx (like the calculator demo)
- Remote servers accessible via HTTP/SSE
- Custom MCP servers you build yourself

This example demonstrates connecting to an external MCP server endpoint.
"""

import asyncio
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from agent_framework.azure import AzureOpenAIChatClient
from agent_framework import MCPStdioTool

# Load environment variables
load_dotenv()

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")

# External MCP server configuration
# For this demo, we'll use a local MCP server that could be run externally
# In a real scenario, this could be a URL like: https://mcp.example.com
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "")


@asynccontextmanager
async def start_external_mcp_server():
    """
    Connect to an external MCP server.
    
    For this demo, we'll start a local MCP server as an example.
    In production, you would connect to a remote MCP server via HTTP/SSE.
    
    Example remote connection (not implemented in this demo):
    - SSE endpoint: https://mcp.example.com/events
    - HTTP endpoint: https://mcp.example.com/api
    """
    # For this demo, we'll use the filesystem MCP server as an example
    # In a real scenario, you'd connect to your external server
    
    from utils.uv_utils import resolve_uvx
    
    uvx_cmd = resolve_uvx()
    print(f"Starting external MCP server simulation...")
    print(f"Command: {uvx_cmd} mcp-server-filesystem --allowed-directory /tmp")
    
    async with MCPStdioTool(
        name="filesystem",
        command=uvx_cmd,
        args=["mcp-server-filesystem", "--allowed-directory", "/tmp"],
    ) as mcp_server:
        print("✅ External MCP server connected!\n")
        print("Note: In production, you would connect to a remote MCP server")
        print("      via HTTP/SSE instead of starting a local process.\n")
        yield mcp_server


async def main():
    """Interactive demo: Agent with external MCP server."""
    
    print("\n" + "="*70)
    print("🌐 DEMO: External MCP Server Integration")
    print("="*70)
    print("""
This demo shows how to connect to an EXTERNAL MCP server.

MCP (Model Context Protocol) allows agents to connect to:
- Local MCP servers (like this demo)
- Remote MCP servers via HTTP/SSE
- Custom tool servers you build

For this demo, we're using a filesystem MCP server as an example.
In production, you would connect to your external MCP endpoint.

Example use cases:
- Company-specific tool servers
- Shared MCP infrastructure
- Third-party MCP services
- Custom protocol implementations

REQUIREMENTS:
- Install 'uv': pip install uv
- MCP server will be installed automatically via 'uvx'
    """)
    
    try:
        input("Press Enter to connect to external MCP server...")
    except EOFError:
        print("\n(Non-interactive environment detected; continuing...)")
    
    try:
        print("\nConnecting to external MCP server...")
        
        async with start_external_mcp_server() as mcp_server:
            
            # Create agent with external MCP tools
            print("Creating agent with external MCP tools...")
            agent = AzureOpenAIChatClient(
                endpoint=ENDPOINT,
                deployment_name=DEPLOYMENT,
                api_key=API_KEY,
                api_version=API_VERSION
            ).create_agent(
                instructions=(
                    "You are a helpful assistant with access to filesystem tools via an external MCP server. "
                    "Use the tools to help users with file operations. "
                    "Always explain what you're doing and ask for confirmation for destructive operations."
                ),
                name="ExternalMCPBot",
                tools=mcp_server
            )
            
            print("✅ Agent ready with external MCP tools!\n")
            
            print("="*70)
            print("INTERACTIVE MODE")
            print("="*70)
            print("""
Example queries:
1. "List files in /tmp"
2. "Read the contents of /tmp/test.txt"
3. "Create a file in /tmp with some content"
4. "Search for .txt files in /tmp"

Note: This demo uses a filesystem MCP server for demonstration.
      In production, replace with your external MCP endpoint.

Type 'quit' to exit
            """)
            
            while True:
                try:
                    user_input = input("\n💭 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("\n✅ Goodbye!")
                        break
                    
                    print("\n🤖 Agent: ", end="", flush=True)
                    async for chunk in agent.run_stream(user_input):
                        if chunk.text:
                            print(chunk.text, end="", flush=True)
                    print("\n")
                    
                except KeyboardInterrupt:
                    print("\n\n✅ Exiting...")
                    break
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    
    except KeyboardInterrupt:
        print("\n✅ Exiting... Goodbye!")
        return
    except asyncio.CancelledError:
        print("\n✅ Exiting... Goodbye!")
        return
    except FileNotFoundError:
        print("\n❌ ERROR: 'uvx' command not found!")
        print("\nSOLUTION:")
        print("1. Install 'uv': pip install uv")
        print("2. Or install with pipx: pipx install uv")
        print("3. Documentation: https://docs.astral.sh/uv/")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTROUBLESHOOTING:")
        print("1. Check 'uv' is installed: uv --version")
        print("2. Verify external MCP server is accessible")
        print("3. Check network connectivity")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Exiting... Goodbye!")
    except asyncio.CancelledError:
        print("\n✅ Exiting... Goodbye!")
