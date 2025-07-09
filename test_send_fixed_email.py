"""
Test the fixed email sending functionality
"""

import os
from email_utils.sendgrid_client import send_test_email

def main():
    print("Testing the fixed SendGrid email client...")
    
    # Set a custom test message
    test_message = """
Testing the fixed SendGrid email client.
This email should be sent successfully with the flat structure.
    """
    
    # Send test email
    result = send_test_email(test_message)
    
    # Print result
    print("Result:", result)
    
    if result.get("success"):
        print("✓ Success! Email was sent successfully.")
    else:
        print("✗ Error:", result.get("error"))
        
if __name__ == "__main__":
    main()
