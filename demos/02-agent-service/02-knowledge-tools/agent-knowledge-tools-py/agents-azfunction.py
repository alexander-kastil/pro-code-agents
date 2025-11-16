import json
import os
from typing import Any, Dict, Optional

import requests
from azure.ai.agents.models import FunctionTool, ToolSet, MessageRole
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def convert_currency_via_function(
    from_currency: str,
    to_currency: str,
    amount: float,
    date: Optional[str] = None,
) -> str:

    FUNCTION_DEPLOYMENT_URL = os.getenv("FUNCTION_DEPLOYMENT_URL")

    normalized_from = from_currency.upper()
    normalized_to = to_currency.upper()

    payload: Dict[str, Any] = {
        "from": normalized_from,
        "to": normalized_to,
        "amount": float(amount),
    }

    if date:
        payload["date"] = date

    response = requests.post(FUNCTION_DEPLOYMENT_URL.rstrip("/"), json=payload, timeout=20)
    response.raise_for_status()

    conversion = response.json()

    summary = (
        f"{payload['amount']} {normalized_from} equals "
        f"{conversion.get('result')} {normalized_to} on {conversion.get('date')}"
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
        agents_client = project_client.agents
        agent = agents_client.create_agent(
            model=model,
            name="currency-conversion-agent",
            instructions=(
                "You assist with currency conversion questions by calling the convert_currency_via_function."
                "Always call the tool when a user provides currencies or amounts."
            ),
            toolset=toolset,
        )

        thread = agents_client.threads.create()
        print(f"You're chatting with: {agent.name} ({agent.id})")

        try:
            default_example = "Exchange 100 EUR to THB"
            prompt_text = (
                "What currency do you want to exchang? Example. Exchange 100 EUR to THB. "
                "Press Enter to accept or Enter your own prompt"
            )
            while True:
                raw = input(f"{prompt_text}\n> ")
                user_prompt = default_example if raw.strip() == "" else raw
                if user_prompt.lower() == "quit":
                    break

                agents_client.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_prompt,
                )

                run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

                if run.status == "failed":
                    print(f"Run failed: {run.last_error}")
                    continue

                last_msg = agents_client.messages.get_last_message_text_by_role(
                    thread_id=thread.id, role=MessageRole.AGENT
                )
                if last_msg:
                    print(f"Assistant: {last_msg.text.value}")
        finally:
            project_client.agents.delete_agent(agent.id)
            # Updated for current SDK: delete thread via threads client
            project_client.agents.threads.delete(thread.id)


if __name__ == "__main__":
    main()
