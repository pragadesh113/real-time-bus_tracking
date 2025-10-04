from flask import Flask, request, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Twilio credentials from environment variables
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID_ALT")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN_ALT")
TWILIO_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER_ALT")

# Initialize Twilio client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

@app.route('/incoming-call', methods=['POST'])
def incoming_call():
    """Handle incoming calls and send an SMS."""
    caller_number = request.form['From']  # The phone number of the caller

    # Send SMS to the caller
    try:
        message = client.messages.create(
            body=f"Hello! Thanks for calling from {caller_number}. We appreciate it!",
            from_=TWILIO_NUMBER,
            to=caller_number
        )
        print(f"SMS sent: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

    # Respond to the call (optional)
    response = VoiceResponse()
    response.say("Thank you for calling. An SMS has been sent to your number.")
    return Response(str(response), mimetype="text/xml")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
