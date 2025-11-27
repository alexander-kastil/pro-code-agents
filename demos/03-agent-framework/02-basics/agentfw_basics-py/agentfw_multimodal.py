"""
Multimodal Content - Image (JPEG) Invoice Extraction (Demo)

This demo shows how to process a JPEG invoice image and extract structured
data using Azure AI Foundry's vision capabilities with the Responses API.
The agent loads the invoice image directly and extracts invoice data as JSON.
"""

import os
import json
import base64
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

# Load environment variables
load_dotenv()

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
delete_resources = os.getenv("DELETE", "true").lower() == "true"

DATA_PATH = os.getenv("DATA_PATH", "./data")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "./output")


# Define structured output model for invoice data
class InvoiceItem(BaseModel):
    """Individual line item on invoice."""
    item: str
    description: str | None = None
    quantity: float | None = None
    unit_price: float | None = None
    total: float | None = None


class InvoiceData(BaseModel):
    """Extract complete invoice information from document."""
    invoice_number: str | None = Field(None, description="Invoice number")
    date: str | None = Field(None, description="Invoice date")
    due_date: str | None = Field(None, description="Payment due date")
    vendor_name: str | None = Field(None, description="Vendor/company name")
    customer_name: str | None = Field(None, description="Customer name")
    items: list[InvoiceItem] = Field(default_factory=list, description="Line items")
    subtotal: float | None = Field(None, description="Subtotal amount")
    tax: float | None = Field(None, description="Tax amount")
    total: float | None = Field(None, description="Total amount")
    payment_terms: str | None = Field(None, description="Payment terms")


def main():
    """Demo: Extract structured invoice data from JPEG using Foundry Responses API."""
    
    print("\n" + "="*70)
    print("📄 DEMO: Multimodal JPEG Invoice Extraction (Foundry)")
    print("="*70)
    
    # Ensure output directory exists
    Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
    
    # Check for invoice JPEG
    invoice_image_path = os.path.join(DATA_PATH, "invoice.jpg")
    if not os.path.exists(invoice_image_path):
        print(f"\n❌ Error: Invoice image not found at {invoice_image_path}")
        print("Please ensure invoice.jpg exists in the data directory.")
        return

    print(f"\n📂 Loading invoice image: {invoice_image_path}")

    # Load JPEG as base64
    print("🔄 Preparing JPEG data URI...")
    with open(invoice_image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")
    print("✅ JPEG loaded and encoded to base64")
    
    # Initialize project client and OpenAI responses client
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client = project_client.get_openai_client()
    
    with project_client:
        # =================================================================
        # OPTION 1: WITH STRUCTURED OUTPUT (Using Pydantic Model)
        # =================================================================
        print("\n" + "="*70)
        print("📋 OPTION 1: With Structured Output (Pydantic Model)")
        print("="*70)
        
        agent_structured = project_client.agents.create_version(
            agent_name="invoice-extractor-structured",
            definition=PromptAgentDefinition(
                model=model,
                instructions=(
                    "You are an expert invoice processing assistant. "
                    "Extract all invoice information accurately from the provided image. "
                    "Pay attention to all fields including items, prices, and totals. "
                    "ALWAYS respond with a JSON object containing these fields:\n"
                    "{\n"
                    '  "invoice_number": "string or null",\n'
                    '  "date": "string or null",\n'
                    '  "due_date": "string or null",\n'
                    '  "vendor_name": "string or null",\n'
                    '  "customer_name": "string or null",\n'
                    '  "items": [{"item": "string", "description": "string", "quantity": number, "unit_price": number, "total": number}],\n'
                    '  "subtotal": number or null,\n'
                    '  "tax": number or null,\n'
                    '  "total": number or null,\n'
                    '  "payment_terms": "string or null"\n'
                    "}\n"
                    "Return ONLY the JSON, no markdown code blocks or extra text."
                )
            )
        )
        
        print(f"\nStructured agent created: {agent_structured.name}")
        
        print("\n🔄 Processing JPEG with structured output...")
        response_structured = openai_client.responses.create(
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Please extract all invoice information from this document and return it as structured JSON data."},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{b64_image}"
                        }
                    ]
                }
            ],
            extra_body={"agent": {"type": "agent_reference", "name": agent_structured.name, "version": agent_structured.version}}
        )
        
        if response_structured.status == "completed":
            for item in response_structured.output:
                if item.type == "message" and item.content and item.content[0].type == "output_text":
                    response_text = item.content[0].text.strip()
                    
                    try:
                        # Clean up potential markdown code blocks
                        json_text = response_text
                        if json_text.startswith("```"):
                            json_text = json_text.split("```")[1]
                            if json_text.startswith("json"):
                                json_text = json_text[4:]
                            json_text = json_text.strip()
                        
                        # Parse JSON and validate with Pydantic
                        data = json.loads(json_text)
                        invoice = InvoiceData(**data)
                        
                        print("\n" + "="*70)
                        print("📊 Extracted Invoice Information:")
                        print("="*70)
                        
                        print(f"\n📋 Invoice Details:")
                        print(f"   Invoice Number: {invoice.invoice_number}")
                        print(f"   Date: {invoice.date}")
                        print(f"   Due Date: {invoice.due_date}")
                        print(f"   Vendor: {invoice.vendor_name}")
                        print(f"   Customer: {invoice.customer_name}")
                        
                        if invoice.items:
                            print(f"\n📦 Items ({len(invoice.items)}):")
                            for i, inv_item in enumerate(invoice.items, 1):
                                print(f"   {i}. {inv_item.item}")
                                if inv_item.description:
                                    print(f"      Description: {inv_item.description}")
                                if inv_item.quantity is not None and inv_item.unit_price is not None and inv_item.total is not None:
                                    print(f"      Qty: {inv_item.quantity} x ${inv_item.unit_price:.2f} = ${inv_item.total:.2f}")
                        
                        print(f"\n💰 Totals:")
                        if invoice.subtotal is not None:
                            print(f"   Subtotal: ${invoice.subtotal:.2f}")
                        if invoice.tax is not None:
                            print(f"   Tax: ${invoice.tax:.2f}")
                        if invoice.total is not None:
                            print(f"   Total: ${invoice.total:.2f}")
                        
                        if invoice.payment_terms:
                            print(f"\n📝 Payment Terms: {invoice.payment_terms}")
                        
                        # Save to JSON file
                        output_file_structured = os.path.join(OUTPUT_PATH, "invoice_structured.json")
                        with open(output_file_structured, 'w') as f:
                            json.dump(invoice.model_dump(), f, indent=2)
                        
                        print(f"\n✅ Structured data saved to: {output_file_structured}")
                        
                    except json.JSONDecodeError as e:
                        print(f"\n❌ Failed to parse JSON: {e}")
                        print(f"Raw response: {response_text[:500]}")
                    except Exception as e:
                        print(f"\n❌ Validation error: {e}")
        else:
            print(f"\n❌ Response failed: {response_structured.status}")
        
        # =================================================================
        # OPTION 2: WITHOUT STRUCTURED OUTPUT (Schemaless - Just Prompting)
        # =================================================================
        print("\n" + "="*70)
        print("📋 OPTION 2: Without Structured Output (Schemaless - Prompt Only)")
        print("="*70)
        
        agent_unstructured = project_client.agents.create_version(
            agent_name="invoice-extractor-unstructured",
            definition=PromptAgentDefinition(
                model=model,
                instructions=(
                    "You are an expert invoice processing assistant. "
                    "Extract all invoice information accurately from the provided image. "
                    "ALWAYS return your response as valid JSON with this structure:\n"
                    "{\n"
                    '  "invoice_number": "string",\n'
                    '  "date": "string",\n'
                    '  "due_date": "string",\n'
                    '  "vendor_name": "string",\n'
                    '  "customer_name": "string",\n'
                    '  "items": [{"item": "string", "description": "string", "quantity": number, "unit_price": number, "total": number}],\n'
                    '  "subtotal": number,\n'
                    '  "tax": number,\n'
                    '  "total": number,\n'
                    '  "payment_terms": "string"\n'
                    "}\n"
                    "Return ONLY the JSON, no markdown code blocks or extra text."
                )
            )
        )
        
        print(f"\nUnstructured agent created: {agent_unstructured.name}")
        
        print("\n🔄 Processing JPEG without structured output (no response_format)...")
        response_unstructured = openai_client.responses.create(
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Extract all invoice information from this document and return as JSON."},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{b64_image}"
                        }
                    ]
                }
            ],
            extra_body={"agent": {"type": "agent_reference", "name": agent_unstructured.name, "version": agent_unstructured.version}}
        )
        
        if response_unstructured.status == "completed":
            for item in response_unstructured.output:
                if item.type == "message" and item.content and item.content[0].type == "output_text":
                    response_text = item.content[0].text.strip()
                    
                    print("\n📄 Raw Response (first 500 chars):")
                    print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                    
                    # Try to parse the JSON from the response
                    try:
                        # Clean up potential markdown code blocks
                        json_text = response_text
                        if json_text.startswith("```"):
                            json_text = json_text.split("```")[1]
                            if json_text.startswith("json"):
                                json_text = json_text[4:]
                            json_text = json_text.strip()
                        
                        invoice_data = json.loads(json_text)
                        
                        print("\n✅ Successfully parsed JSON!")
                        print("\n📊 Extracted Invoice Information:")
                        print(f"   Invoice Number: {invoice_data.get('invoice_number')}")
                        print(f"   Date: {invoice_data.get('date')}")
                        print(f"   Vendor: {invoice_data.get('vendor_name')}")
                        print(f"   Customer: {invoice_data.get('customer_name')}")
                        print(f"   Total: ${invoice_data.get('total')}")
                        
                        # Save to JSON file
                        output_file_unstructured = os.path.join(OUTPUT_PATH, "invoice_unstructured.json")
                        with open(output_file_unstructured, 'w') as f:
                            json.dump(invoice_data, f, indent=2)
                        
                        print(f"\n✅ Unstructured data saved to: {output_file_unstructured}")
                        
                    except json.JSONDecodeError as e:
                        print(f"\n❌ Failed to parse JSON: {e}")
                        print("⚠️  The LLM didn't return valid JSON - this is the risk of schemaless!")
        else:
            print(f"\n❌ Response failed: {response_unstructured.status}")
        
        # =================================================================
        # COMPARISON SUMMARY
        # =================================================================
        print("\n" + "="*70)
        print("📊 COMPARISON: Schema (Model) vs Schemaless (No Model)")
        print("="*70)
        print("\n✅ WITH Pydantic Model (response_format=InvoiceData):")
        print("   • LLM is instructed to return data matching your exact schema")
        print("   • Better JSON structure - consistent field names")
        print("   • Type validation and conversion (strings, floats, etc.)")
        print("   • Direct access to typed fields: invoice.invoice_number")
        print("   • Handles optional fields with None values")
        print("   • Production-ready and reliable")
        print("\n⚠️  WITHOUT Pydantic Model (schemaless - just prompting):")
        print("   • LLM MIGHT wrap JSON in markdown code blocks")
        print("   • No guaranteed structure - fields might be missing")
        print("   • Need manual JSON parsing with try/except error handling")
        print("   • LLM might ignore your format request")
        print("   • More fragile and error-prone")
        print("   • Risk of inconsistent responses")
        print("\n🎯 RECOMMENDATION:")
        print("   Always use Pydantic models (schema) for structured data extraction!")
        print("   The model IS the schema - it's not optional for production use.")
        
        print("\n" + "="*70)
        
        # Cleanup based on DELETE flag
        if delete_resources:
            project_client.agents.delete_version(agent_name=agent_structured.name, agent_version=agent_structured.version)
            project_client.agents.delete_version(agent_name=agent_unstructured.name, agent_version=agent_unstructured.version)
            print("Deleted agent versions")
        else:
            print(f"Agents preserved: {agent_structured.name}, {agent_unstructured.name}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Process interrupted.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
