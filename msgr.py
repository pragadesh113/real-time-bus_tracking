from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Twilio credentials from environment variables
account_sid = os.environ.get("TWILIO_ACCOUNT_SID_ALT")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN_ALT")
twilio_number = os.environ.get("TWILIO_PHONE_NUMBER_ALT")

# Initialize Twilio client
client = Client(account_sid, auth_token)

# Function to send SMS
def send_sms(to_number, message_body):
    try:
        message = client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=to_number
        )
        print(f"Message sent to {to_number}: {message.sid}")
    except Exception as e:
        print(f"Failed to send message to {to_number}: {str(e)}")

# Example usage
to_number = "+917603848442"  # Replace with the recipient's phone number
message_body = "Hello, this is a test message from your Twilio setup!"

send_sms(to_number, message_body)
