#include <ESP8266WiFi.h>
#include <FirebaseESP8266.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>

// Wi-Fi credentials
const char* ssid = "s21fe";           // Replace with your Wi-Fi SSID
const char* password = "ziry2240";    // Replace with your Wi-Fi password

// Firebase configuration
FirebaseConfig config;
FirebaseAuth auth;
FirebaseData firebaseData; // Add this to handle Firebase operations

// GPS module connections
#define RXPin D1 // GPS TX connected to NodeMCU D1 (GPIO5)
#define TXPin D2 // GPS RX connected to NodeMCU D2 (GPIO4)
SoftwareSerial gpsSerial(RXPin, TXPin); // SoftwareSerial for GPS communication
TinyGPSPlus gps; // TinyGPS++ object for GPS data parsing

void setup() {
  // Start Serial Monitor
  Serial.begin(115200);
  Serial.println();

  // Initialize GPS communication
  gpsSerial.begin(9600); // GPS baud rate

  // Connect to Wi-Fi
  Serial.print("WiFi connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi Connected Successfully!");
  Serial.print("NodeMCU IP Address: ");
  Serial.println(WiFi.localIP());

  // Configure Firebase
  config.host = "bus-live-tracking-default-rtdb.firebaseio.com"; // Your Firebase database URL
  config.signer.tokens.legacy_token = "KPyQxHrJ70NKyvtPKcKeyYo0uIluZkUiZHJdcWrw"; // Your Firebase secret key

  // Initialize Firebase
  Firebase.begin(&config, &auth);
  Serial.println("Firebase initialized!");
}

void loop() {
  double latitude = 0.0, longitude = 0.0;

  // Read GPS data
  while (gpsSerial.available() > 0) {
    char c = gpsSerial.read();
    if (gps.encode(c)) { // Check if valid GPS data is available
      if (gps.location.isUpdated()) {
        latitude = gps.location.lat();
        longitude = gps.location.lng();
      }
    }
  }

  // Print GPS data to Serial Monitor
  Serial.print("Latitude: ");
  Serial.println(latitude, 6); // 6 decimal places for precision
  Serial.print("Longitude: ");
  Serial.println(longitude, 6);

  // Update latitude and longitude in Firebase
  if (Firebase.setDouble(firebaseData, "/bus/location/latitude", latitude)) {
    Serial.println("Latitude updated successfully in Firebase!");
  } else {
    Serial.print("Error updating latitude: ");
    Serial.println(firebaseData.errorReason());
  }

  if (Firebase.setDouble(firebaseData, "/bus/location/longitude", longitude)) {
    Serial.println("Longitude updated successfully in Firebase!");
  } else {
    Serial.print("Error updating longitude: ");
    Serial.println(firebaseData.errorReason());
  }

  // Wait for 30 seconds before the next update
  delay(30000);
}
