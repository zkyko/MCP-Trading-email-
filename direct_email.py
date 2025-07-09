"""
Direct email sender for trade alerts - bypasses all existing email infrastructure
"""
import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_direct_email(message_content="Test email from trading system"):
    """
    Send email directly using SendGrid, bypassing all existing email code
    """
    try:
        # Get environment variables
        api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("FROM_EMAIL") 
        to_email = os.getenv("TO_EMAIL")
        
        if not all([api_key, from_email, to_email]):
            return {"error": "Missing email configuration", "success": False}
        
        # Create the email message
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject="Direct Email Test - ASCII Only",
            plain_text_content=str(message_content)
        )
        
        # Send the email
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        return {
            "success": True,
            "status_code": response.status_code,
            "message": f"Email sent to {to_email}"
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}
