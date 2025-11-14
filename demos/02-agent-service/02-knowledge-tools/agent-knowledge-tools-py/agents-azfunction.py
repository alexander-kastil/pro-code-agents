import json
import os
import sys
from typing import Any, Dict, Optional

import requests
from azure.ai.agents.models import FunctionTool, ToolSet
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def convert_currency_via_function(
    from_currency: str,
    to_currency: str,
    amount: float,
    date: Optional[str] = None,
) -> str:
    """Convert currency by calling the deployed Azure Function endpoint."""

    FUNCTION_DEPLOYMENT_URL = os.getenv("FUNCTION_DEPLOYMENT_URL")
    if not FUNCTION_DEPLOYMENT_URL:
        raise ValueError(
            "FUNCTION_DEPLOYMENT_URL is not set. Update .env with the Azure Function endpoint."
        )

    normalized_from = from_currency.upper()
    normalized_to = to_currency.upper()

    payload: Dict[str, Any] = {
        "from": normalized_from,
        "to": normalized_to,
        "amount": float(amount),
    }

    if date:
        payload["date"] = date

    try:
        response = requests.post(FUNCTION_DEPLOYMENT_URL.rstrip("/"), json=payload, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ValueError(f"Currency conversion failed: {exc}") from exc

    conversion = response.json()

    if "result" not in conversion:
        raise ValueError("Azure Function response did not include a conversion result.")

    summary = (
        f"{payload['amount']} {normalized_from} equals "
        f"{conversion['result']} {normalized_to} on {conversion.get('date')}"
    )

    return json.dumps({
        "summary": summary,
        "details": conversion,
    })


def main() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    load_dotenv()

    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")

    if not endpoint or not model:
        print("PROJECT_ENDPOINT and MODEL_DEPLOYMENT must be set in .env", file=sys.stderr)
        sys.exit(1)

    if not os.getenv("FUNCTION_DEPLOYMENT_URL"):
        print("FUNCTION_DEPLOYMENT_URL must be set in .env", file=sys.stderr)
        sys.exit(1)

    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")
    print("Azure Function endpoint:", os.getenv("FUNCTION_DEPLOYMENT_URL"))

    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    toolset = ToolSet()
    toolset.add(FunctionTool({convert_currency_via_function}))

    with project_client:
        agent = project_client.agents.create_agent(
            model=model,
            name="currency-conversion-agent",
            instructions=(
                "You assist with currency conversion questions by calling the convert_currency_via_function."
                "Always call the tool when a user provides currencies or amounts."
            ),
            toolset=toolset,
        )

        thread = project_client.agents.threads.create()
        print(f"You're chatting with: {agent.name} ({agent.id})")

        try:
            while True:
                user_prompt = input("Prompt (type 'quit' to exit): ")
                if user_prompt.lower() == "quit":
                    break
                if not user_prompt.strip():
                    print("Please enter a prompt.")
                    continue

                project_client.agents.create_message(
                    thread_id=thread.id,
                    role="user",
                    content=user_prompt,
                )

                run = project_client.agents.create_and_process_run(
                    thread_id=thread.id,
                    agent_id=agent.id,
                )

                if run.status == "failed":
                    print(f"Run failed: {run.last_error}")
                    continue

                messages = project_client.agents.list_messages(thread_id=thread.id)
                last_msg = messages.get_last_text_message_by_role("assistant")
                if last_msg:
                    print(f"Assistant: {last_msg.text.value}")
        finally:
            project_client.agents.delete_agent(agent.id)
            project_client.agents.delete_thread(thread.id)


if __name__ == "__main__":
    main()
