import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env
dotenv_path = Path('.') / '.env'
load_dotenv(dotenv_path=dotenv_path)

API_KEY = os.getenv("API_KEY")
GEO_KEY = os.getenv("GEO_KEY")

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"

def get_coordinates_mapbox(query, limit=1):

    # URL-encodes the query 
    url = f"{MAPBOX_BASE_URL}/{query}.json"
    params = {
        'access_token': GEO_KEY,
        'limit': limit,
    }# mudar eso del strip, borrar comentarios, hacer excepciones, 

    response = requests.get(url, params=params)
    #print(f“[DEBUG] Mapbox response geocoding: {response}”)

    if response.status_code == 200:
        data = response.json()
        features = data.get('features', [])
        if not features:
            print("No results were found in Mapbox for that query.")
            return None, None

        # We take the first result
        feature = features[0]
        coords = feature.get('center', None)
        if coords:
            lon, lat = coords[0], coords[1]
            return lat, lon
        else:
            print("No coordinates were found in the result.")
            return None, None
    else:
        print(f'Error in Mapbox query. Code: {response.status_code}')
        print(response.text)
        return None, None




def get_weather(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'en'
    }
    response = requests.get(WEATHER_URL, params=params)
    print(f"[DEBUG] Weather response: {response}")

    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        return temp, description
    else:
        print(f"Error in weather request. Code: {response.status_code}")
        print(response.text)
        return None, None


if __name__ == "__main__":
    query_type = input("Search by name, ZIP code, landmark('general') or GPS ('GPS')?: ").strip().lower()

    if query_type == 'gps':
        lat = input("Enter latitude: ")
        lon = input("Enter longitude: ")

    elif query_type == 'general':
        query = input("Name |Zip Code (6200-101,PT) | Landmark (Eiffel Tower): ")
        
        lat, lon = get_coordinates_mapbox(query)

    else:
        print("Invalid option. Use 'general' or 'GPS'.")
        exit(1)

    if lat is not None and lon is not None:
        temp, description = get_weather(lat, lon)
        if temp is not None:
            print(f"Coordinates: lat={lat}, lon={lon}")
            print(f"Current temperature: {temp}°C")
            print(f"Weather: {description.capitalize()}")
