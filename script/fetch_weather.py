import sys
import requests
import json

def fetch_weather(location_name, latitude, longitude):
    API_URL = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps({"location": location_name, "api_url": API_URL, "data": data}, indent=4))
    else:
        print(f"Error al obtener datos de {location_name}: {response.status_code}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    locations = {
        "madrid": {"latitude": 40.4165, "longitude": -3.70256},
        "paris": {"latitude": 48.8566, "longitude": 2.3522}
    }
    
    if len(sys.argv) != 2 or sys.argv[1] not in locations:
        print("Uso: python fetch_weather.py [madrid|paris]", file=sys.stderr)
        sys.exit(1)
    
    location = sys.argv[1]
    fetch_weather(location, locations[location]["latitude"], locations[location]["longitude"])
