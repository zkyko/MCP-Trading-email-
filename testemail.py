from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

message = Mail(
    from_email='genjishimada771@gmail.com',
    to_emails='nischalbhandari73@gmail.com',
    subject='Test Email',
    html_content='<strong>Hello from SendGrid!</strong>'
)

try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(f"Error: {e}")
