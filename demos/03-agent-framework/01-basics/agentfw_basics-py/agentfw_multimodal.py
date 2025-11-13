"""
NEW 09: Multimodal Content - PDF Invoice Extraction (Demo)

This demo shows how to process PDF documents and extract structured data
using Azure OpenAI's vision capabilities with the Agent Framework.
The agent converts PDF to images and extracts invoice data as JSON.
"""

import asyncio
import os
import base64
import json
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pdf2image import convert_from_path
from io import BytesIO

from agent_framework.azure import AzureOpenAIChatClient
from agent_framework._types import ChatMessage, TextContent, UriContent

# Load environment variables
load_dotenv()

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")
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


def pdf_to_base64_image(pdf_path: str) -> str:
    """Convert first page of PDF to base64-encoded PNG image.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Base64-encoded PNG image string
    """
    # Convert PDF to images (first page only)
    images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=200)
    
    # Convert to base64
    buffer = BytesIO()
    images[0].save(buffer, format="PNG")
    image_bytes = buffer.getvalue()
    return base64.b64encode(image_bytes).decode("utf-8")


async def main():
    """Demo: Extract structured invoice data from PDF."""
    
    print("\n" + "="*70)
    print("📄 DEMO: Multimodal PDF Invoice Extraction")
    print("="*70)
    
    # Ensure output directory exists
    Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
    
    # Check for invoice PDF
    invoice_path = os.path.join(DATA_PATH, "invoice.pdf")
    if not os.path.exists(invoice_path):
        print(f"\n❌ Error: Invoice file not found at {invoice_path}")
        print("Please ensure invoice.pdf exists in the data directory.")
        return
    
    print(f"\n📂 Loading invoice: {invoice_path}")
    
    # Convert PDF to base64 image
    print("🔄 Converting PDF to image...")
    image_base64 = pdf_to_base64_image(invoice_path)
    image_data_url = f"data:image/png;base64,{image_base64}"
    
    print("✅ PDF converted to image")
    
    # Create agent with vision capabilities
    agent = AzureOpenAIChatClient(
        endpoint=ENDPOINT,
        deployment_name=DEPLOYMENT,
        api_key=API_KEY,
        api_version=API_VERSION
    ).create_agent(
        instructions=(
            "You are an expert invoice processing assistant. "
            "Extract all invoice information accurately from the provided image. "
            "Pay attention to all fields including items, prices, and totals."
        ),
        name="InvoiceExtractorBot"
    )
    
    print("✅ Agent created with InvoiceData schema")
    
    # Prepare multimodal message with image
    print("\n🔄 Processing invoice with vision model...")
    
    # Create message with both text and image content using Agent Framework types
    user_message = ChatMessage(
        role="user",
        contents=[
            TextContent(text="Please extract all invoice information from this document and return it as structured data."),
            UriContent(uri=image_data_url, media_type="image/png")
        ]
    )
    
    # Get structured response
    response = await agent.run(user_message, response_format=InvoiceData)
    
    if response.value:
        invoice = response.value
        
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
            for i, item in enumerate(invoice.items, 1):
                print(f"   {i}. {item.item}")
                if item.description:
                    print(f"      Description: {item.description}")
                if item.quantity is not None and item.unit_price is not None:
                    print(f"      Qty: {item.quantity} × ${item.unit_price:.2f} = ${item.total:.2f}")
        
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
        output_file = os.path.join(OUTPUT_PATH, "invoice_extracted.json")
        with open(output_file, 'w') as f:
            json.dump(invoice.model_dump(), f, indent=2)
        
        print(f"\n✅ Extracted data saved to: {output_file}")
        
    else:
        print("\n❌ Could not extract invoice information")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Process interrupted.")
    except Exception as e:
        print(f"\n❌ Error: {e}")