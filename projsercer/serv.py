import geocoder
from pymongo import MongoClient
import time

# MongoDB Atlas connection setup
MONGO_URI = "mongodb+srv://pragadesh:hsedagarp@cluster0.pemkq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['bustracking']
collection = db['locations']

def get_current_location():
    """
    Fetches the current geographical location (latitude, longitude) of the laptop.
    """
    try:
        # Get current location using geocoder's IP method (fallback if GPS is not available)
        g = geocoder.ip('me')
        if g.ok:
            return g.latlng
        else:
            print("Could not retrieve location. Please check your internet connection.")
            return None
    except Exception as e:
        print(f"Error fetching location: {e}")
        return None

def push_location_to_db(lat, lng):
    """
    Inserts the latitude and longitude into the MongoDB database.
    """
    try:
        # Insert the coordinates into the MongoDB collection
        data = {
            'location': {
                'latitude': lat,
                'longitude': lng
            }
        }
        result = collection.insert_one(data)
        print(f"Inserted document with ID: {result.inserted_id}")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

def main():
    while True:
        # Get current location
        coordinates = get_current_location()
        if coordinates:
            lat, lng = coordinates
            print(f"Current Location - Latitude: {lat}, Longitude: {lng}")
            
            # Push the coordinates to the MongoDB
            push_location_to_db(lat, lng)
        
        # Wait for 10 seconds before fetching location again
        time.sleep(10)

if __name__ == "__main__":
    print("Starting location updater...")
    main()
#get current time and push along with lat anf long to db
#get loc every 1 min once 