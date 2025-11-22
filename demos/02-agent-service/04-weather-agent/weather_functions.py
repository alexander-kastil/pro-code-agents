"""
Weather-related functions for the Azure Weather Agent.

These functions simulate weather data retrieval and email notifications.
In a production scenario, these would integrate with real weather APIs
and email services.
"""

import os
import json
from datetime import datetime
from typing import Annotated


def get_weather(location: Annotated[str, "The location to get the weather for"]) -> str:
    """
    Get the current weather for a given location.
    
    Args:
        location: The location to get the weather for (e.g., "Seattle", "London")
        
    Returns:
        A string describing the current weather conditions
    """
    # Simulated weather data - in production, this would call a real weather API
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    temperature = 53
    
    weather_info = f"The weather in {location} is {conditions[0]} with a high of {temperature}°C."
    
    print(f"🌤️  [Function Call] get_weather(location='{location}')")
    print(f"   → Result: {weather_info}")
    
    return weather_info


def get_forecast(
    location: Annotated[str, "The location to get the forecast for"],
    days: Annotated[int, "Number of days for forecast (1-7)"] = 3
) -> str:
    """
    Get weather forecast for multiple days.
    
    Args:
        location: The location to get the forecast for
        days: Number of days for the forecast (default: 3, max: 7)
        
    Returns:
        A formatted string with the multi-day forecast
    """
    # Ensure days is within reasonable bounds
    days = max(1, min(days, 7))
    
    # Simulated forecast data
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    forecast_lines = []
    
    for day in range(1, days + 1):
        condition = conditions[0]  # In production, this would vary
        temp = 53 + day  # Slight variation for demo
        forecast_lines.append(f"Day {day}: {condition}, {temp}°C")
    
    forecast_text = f"Weather forecast for {location}:\n" + "\n".join(forecast_lines)
    
    print(f"📅 [Function Call] get_forecast(location='{location}', days={days})")
    print(f"   → Result: {len(forecast_lines)} days forecast generated")
    
    return forecast_text


def send_email(
    recipient: Annotated[str, "The email address of the recipient"],
    subject: Annotated[str, "The subject of the email"],
    body: Annotated[str, "The body content of the email"]
) -> str:
    """
    Simulate sending an email with weather information.
    
    NOTE: This requires user approval and will save the email data to a file
    instead of actually sending it.
    
    Args:
        recipient: The email address to send to
        subject: The email subject line
        body: The email body content
        
    Returns:
        A JSON string with the email sending result
    """
    timestamp = datetime.now().isoformat()
    email_id = f"EMAIL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    email_data = {
        "email_id": email_id,
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "timestamp": timestamp,
        "status": "simulated_sent"
    }
    
    # Save email to output directory
    output_path = os.getenv("OUTPUT_PATH", "./output")
    emails_dir = os.path.join(output_path, "emails")
    os.makedirs(emails_dir, exist_ok=True)
    
    filename = os.path.join(emails_dir, f"{email_id}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(email_data, f, indent=2, ensure_ascii=False)
    
    result_message = f"Email sent to {recipient} with subject '{subject}'. Saved to: {filename}"
    
    print(f"📧 [Function Call] send_email(recipient='{recipient}', subject='{subject}')")
    print(f"   → Result: Email saved to {filename}")
    
    return json.dumps({
        "success": True,
        "email_id": email_id,
        "message": result_message,
        "filename": filename
    })


# Export the functions for use by the agent
user_functions = {get_weather, get_forecast, send_email}
