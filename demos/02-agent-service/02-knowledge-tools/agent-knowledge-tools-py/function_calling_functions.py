import os
import json
from datetime import datetime

def get_user_email() -> str:
    """Get the user's email address."""
    return input("Please enter your email address: ")

def get_issue_description() -> str:
    """Get a description of the issue from the user."""
    return input("Please describe the issue: ")

def submit_support_ticket(email: str, issue: str) -> str:
    """
    Submit a support ticket with the user's email and issue description.
    
    Args:
        email: The user's email address
        issue: Description of the technical issue
        
    Returns:
        A JSON string with ticket details
    """
    timestamp = datetime.now().isoformat()
    ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    ticket_data = {
        "ticket_id": ticket_id,
        "email": email,
        "issue": issue,
        "timestamp": timestamp,
        "status": "submitted"
    }
    
    # Save the ticket to a file
    tickets_dir = "support_tickets"
    os.makedirs(tickets_dir, exist_ok=True)
    
    filename = f"{tickets_dir}/{ticket_id}.json"
    with open(filename, "w") as f:
        json.dump(ticket_data, f, indent=2)
    
    return json.dumps({
        "success": True,
        "ticket_id": ticket_id,
        "message": f"Support ticket submitted successfully. File saved: {filename}",
        "filename": filename
    })

# Export the functions for use by the agent
user_functions = {get_user_email, get_issue_description, submit_support_ticket}
