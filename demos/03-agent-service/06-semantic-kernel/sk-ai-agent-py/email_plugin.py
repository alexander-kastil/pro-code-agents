from semantic_kernel.functions import kernel_function
from typing import Annotated

class EmailPlugin:
    """A Plugin to simulate email functionality."""
    
    @kernel_function(description="Sends an email.")
    def send_email(self,
                to: Annotated[str, "Who to send the email to"],
                subject: Annotated[str, "The subject of the email."],
                body: Annotated[str, "The text body of the email."]):
        print("\nTo:", to)
        print("Subject:", subject)
        print(body, "\n")
