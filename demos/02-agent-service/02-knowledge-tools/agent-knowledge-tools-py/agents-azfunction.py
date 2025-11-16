import json
import os
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

    functions = FunctionTool([convert_currency_via_function])
    toolset = ToolSet()
    toolset.add(functions)

    with project_client:
        agent = project_client.agents.create_agent(
            model=model,
            name="currency-conversion-agent",
            instructions=(
                "You assist with currency conversion questions by calling the convert_currency_via_function."
                "Always call the tool when a user provides currencies or amounts."
            ),
            toolset=toolset
        )

        thread = project_client.agents.threads.create()
        print(f"You're chatting with: {agent.name} ({agent.id})")

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

            message = project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=user_prompt
            )
            
            run = project_client.agents.create_and_process_run(
                thread_id=thread.id, 
                agent_id=agent.id
            )

            if run.status == "failed":
                print(f"Run failed: {run.last_error}")
                continue

            messages = project_client.agents.list_messages(thread_id=thread.id)
            last_msg = messages.get_last_text_message_by_role("assistant")
            if last_msg:
                print(f"Assistant: {last_msg.text.value}")

        project_client.agents.delete_agent(agent.id)
        print("Deleted agent")


if __name__ == "__main__":
    main()
