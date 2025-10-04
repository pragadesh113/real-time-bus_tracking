from flask import Flask, render_template, jsonify, request
import pyrebase
from flask_cors import CORS
from twilio.rest import Client
import geopy.distance  # For distance calculation
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Firebase configuration
firebase_config = {
    "apiKey": os.environ.get("FIREBASE_API_KEY"),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
    "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.environ.get("FIREBASE_APP_ID"),
    "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID")
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

# Twilio setup
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_number = os.environ.get("TWILIO_PHONE_NUMBER")
client = Client(account_sid, auth_token)

# Phone numbers from environment variables
phone_numbers_str = os.environ.get("PHONE_NUMBERS", "")
phone_numbers = [num.strip() for num in phone_numbers_str.split(",") if num.strip()]

# Bus stops with coordinates
bus_stops = [
    {"name": "Periar Nilayam", "coords": (9.91576, 78.11070)},
    {"name": "Palanganatham", "coords": (9.90076, 78.09352)},
    {"name": "Thiruparankundram", "coords": (9.88580, 78.07453)},
    {"name": "Thirunagar", "coords": (9.88229, 78.05316)},
    {"name": "Thirumangalam", "coords": (9.82697, 77.99063)}
]

# Track stops that have been notified
notified_stops = set()

def send_sms(phone_numbers, message):
    """Send an SMS using Twilio."""
    for number in phone_numbers:
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=number
        )
    print(f"SMS sent to {phone_numbers}: {message}")  # Debug print

@app.route('/')
def index():
    return render_template('bustracking.html')

@app.route('/get_location_message')
def get_location_message():
    try:
        # Fetch the latest coordinates from Firebase
        location_data = db.child("bus").child("location").get().val()
        print(f"Fetched location data: {location_data}")  # Debug print

        if location_data:
            latitude = location_data.get("latitude", 0.0)
            longitude = location_data.get("longitude", 0.0)

            if latitude == 0.0 or longitude == 0.0:
                return jsonify({"error": "Invalid coordinates in Firebase"}), 400

            # Check proximity to bus stops
            bus_coords = (latitude, longitude)
            check_proximity_and_notify(bus_coords)

            # Return latitude and longitude in JSON format
            return jsonify({
                "latitude": latitude,
                "longitude": longitude
            })
        else:
            return jsonify({"error": "No location data available"}), 404
    except Exception as e:
        print(f"Error generating location message: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/coordinates')
def get_coordinates():
    try:
        # Fetch location data from Firebase
        location_data = db.child("bus").child("location").get().val()
        if location_data:
            latitude = location_data.get("latitude", 0.0)
            longitude = location_data.get("longitude", 0.0)

            # Check proximity to bus stops
            bus_coords = (latitude, longitude)
            check_proximity_and_notify(bus_coords)

            formatted_data = {"latitude": latitude, "longitude": longitude}
            return jsonify(formatted_data)
        else:
            return jsonify({"error": "No location data found"}), 404
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

def check_proximity_and_notify(bus_coords):
    """Check the nearest stop and send SMS if within 2 km."""
    global notified_stops

    nearest_stop = None
    min_distance = float('inf')

    for stop in bus_stops:
        stop_name = stop["name"]
        stop_coords = stop["coords"]

        # Calculate the distance between the bus and the stop
        distance = geopy.distance.distance(bus_coords, stop_coords).km

        # Check if this stop is the closest so far
        if distance < min_distance:
            nearest_stop = stop
            min_distance = distance

    # If the nearest stop is within 2 km and not yet notified
    if nearest_stop and min_distance <= 2.0:
        stop_name = nearest_stop["name"]

        if stop_name not in notified_stops:
            # Send SMS and mark the stop as notified
            message = f"Bus is nearing {stop_name}! (Distance: {min_distance:.2f} km)"
            send_sms(phone_numbers, message)
            notified_stops.add(stop_name)
    else:
        # Clear notified stops if no stop is within 2 km
        notified_stops.clear()


@app.route('/sms', methods=['POST'])
def sms_reply():
    try:
        # Parse the incoming SMS
        incoming_msg = request.form.get('Body').strip().lower()
        from_number = request.form.get('From')

        # Check if the message contains the keyword "buslocation"
        if "buslocation" in incoming_msg:
            # Fetch the latest coordinates from Firebase
            location_data = db.child("bus").child("location").get().val()
            if location_data:
                latitude = location_data.get("latitude", 0.0)
                longitude = location_data.get("longitude", 0.0)

                # Perform reverse geocoding to get the street name
                response = requests.get(reverse_geocode_url, params={"lat": latitude, "lon": longitude})
                geocode_data = response.json()
                street_name = geocode_data.get("address", {}).get("road", "Unknown Street")

                # Prepare the SMS response
                message = f"Bus Location: {street_name}\nLatitude: {latitude}\nLongitude: {longitude}"

                # Send the response to the user
                resp = MessagingResponse()
                resp.message(message)
                return str(resp)
            else:
                resp = MessagingResponse()
                resp.message("Bus location data is not available at the moment.")
                return str(resp)
        else:
            # If the keyword is not found, send a generic response
            resp = MessagingResponse()
            resp.message("Invalid request. Send 'BusLocation' to get the current bus location.")
            return str(resp)
    except Exception as e:
        print(f"Error in SMS handling: {e}")
        resp = MessagingResponse()
        resp.message("An error occurred while processing your request.")
        return str(resp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)