import os
import io
import sys
from dotenv import load_dotenv
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential

# Configure UTF-8 encoding for Windows console (fixes emoji display issues)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    """Delete all agents in the Azure AI Foundry project."""
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")

    print(f"{'='*70}")
    print("🗑️  AGENT DELETION UTILITY")
    print(f"{'='*70}")
    print(f"Endpoint: {endpoint}")
    print()

    agents_client = AgentsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    with agents_client:
        # List all agents
        print("📋 Fetching all agents...")
        agents = agents_client.list_agents()
        
        agent_list = list(agents)
        
        if not agent_list:
            print("\n✅ No agents found. Nothing to delete.")
            return
        
        print(f"\n📊 Found {len(agent_list)} agent(s):")
        print(f"{'─'*70}")
        
        for i, agent in enumerate(agent_list, 1):
            print(f"{i}. {agent.name} (ID: {agent.id})")
            if hasattr(agent, 'description') and agent.description:
                print(f"   Description: {agent.description}")
        
        print(f"{'─'*70}")
        print()
        print("Select agents to delete:")
        print("  - Enter numbers separated by commas (e.g., 1,3,5)")
        print("  - Enter 'all' to delete all agents")
        print("  - Enter 'q' to quit")
        print()
        
        selection = input("Your selection: ").strip().lower()
        
        if selection == 'q':
            print("\n✅ Cancelled. No agents were deleted.")
            return
        
        # Determine which agents to delete
        agents_to_delete = []
        
        if selection == 'all':
            agents_to_delete = agent_list
        else:
            try:
                indices = [int(x.strip()) for x in selection.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(agent_list):
                        agents_to_delete.append(agent_list[idx - 1])
                    else:
                        print(f"⚠️  Invalid selection: {idx} (out of range)")
            except ValueError:
                print("❌ Invalid input format. Please enter numbers separated by commas.")
                return
        
        if not agents_to_delete:
            print("\n✅ No agents selected. Nothing to delete.")
            return
        
        print(f"\n🗑️  Selected {len(agents_to_delete)} agent(s) for deletion:")
        for agent in agents_to_delete:
            print(f"  - {agent.name} (ID: {agent.id})")
        
        print()
        final_confirm = input(f"⚠️  Proceed to delete {len(agents_to_delete)} agent(s)? (yes/no): ").strip().lower()
        
        if final_confirm not in ['yes', 'y']:
            print("\n✅ Cancelled. No agents were deleted.")
            return
        
        print()
        print("🗑️  Deleting agents...")
        print(f"{'─'*70}")
        
        deleted_count = 0
        failed_count = 0
        
        for i, agent in enumerate(agents_to_delete, 1):
            try:
                agents_client.delete_agent(agent.id)
                print(f"✓ [{i}/{len(agents_to_delete)}] Deleted: {agent.name} (ID: {agent.id})")
                deleted_count += 1
            except Exception as e:
                print(f"✗ [{i}/{len(agents_to_delete)}] Failed to delete {agent.name} (ID: {agent.id}): {e}")
                failed_count += 1
        
        print(f"{'─'*70}")
        print()
        print(f"{'='*70}")
        print("📊 SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Successfully deleted: {deleted_count} agent(s)")
        if failed_count > 0:
            print(f"❌ Failed to delete: {failed_count} agent(s)")
        print(f"{'='*70}")


if __name__ == '__main__':
    main()
