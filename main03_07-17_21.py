import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime



dotenv_path = Path('.') / '.env'
load_dotenv(dotenv_path=dotenv_path)


WEATHER_KEY = os.getenv("WEATHER_KEY")
GEO_KEY = os.getenv("GEO_TOKEN")


WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places" 


def get_coordinates_mapbox(query, limit=1):

    url = f"{MAPBOX_BASE_URL}/{query}.json"
    params = {
        'access_token': GEO_KEY,
        'limit': limit,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return extract_coordinates(data)
    except requests.RequestException as e:
        print(f"[ERROR] Mapbox request failed: {e}")
        return None, None


def extract_coordinates(data):
    features = data.get('features', [])
    if not features:
        print("No results were found in Mapbox for that query.")
        return None, None

    feature = features[0]
    coords = feature.get('center', None)
    if coords:
        lon, lat = coords[0], coords[1]
        return lat, lon
    else:
        print("No coordinates were found in the result.")
        return None, None


def parse_weather_response(data):
    try:
        weather_info = {
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'temp_min': data['main']['temp_min'],
            'temp_max': data['main']['temp_max'],
            'pressure': data['main']['pressure'],
            'humidity': data['main']['humidity'],
            'weather_main': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'],
            'weather_icon': data['weather'][0]['icon'],
            'wind_speed': data['wind']['speed'],
            'wind_deg': data['wind'].get('deg'),
            'clouds': data['clouds']['all'],
            'visibility': data.get('visibility'),
            'rain_1h': data.get('rain', {}).get('1h'),
            'snow_1h': data.get('snow', {}).get('1h'),
            'sunrise': data['sys']['sunrise'],
            'sunset': data['sys']['sunset'],
            'city': data['name'],
            'country': data['sys']['country'],
        }
        return weather_info
    except (KeyError, IndexError, TypeError):
        print("[ERROR] Unexpected weather data format.")
        return None


def get_weather(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': WEATHER_KEY,
        'units': 'metric',
        'lang': 'en'
    }

    try:
        response = requests.get(WEATHER_URL, params=params)
        response.raise_for_status()
        return parse_weather_response(response.json())
    except requests.RequestException as e:
        print(f"[ERROR] OpenWeatherMap request failed: {e}")
        return None

def format_unix_time(timestamp):
    try:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except (TypeError, ValueError):
        return "N/A"






if __name__ == "__main__":
    print("Choose search method:")
    print("1 - General (name, ZIP code, landmark)")
    print("2 - GPS (coordinates)")

    option = input("Enter 1 or 2: ").strip()

    query = None;
    if option == '1':
        query = input("Name | Zip Code | Landmark: ")
        lat, lon = get_coordinates_mapbox(query)
    elif option == '2':
        lat = input("Enter latitude: ")
        lon = input("Enter longitude: ")
    else:
        print("Invalid option. Please enter 1 or 2.")
        exit(1)



    

    
    

    if lat is not None and lon is not None:
        weather = get_weather(lat, lon)
        if weather is not None:
            print(f"📍Coordinates: lat={lat}, lon={lon}")
            print(f"🏙️City: {weather['city']}, {weather['country']}")
            print(f"🌡️Temperature: {weather['temperature']}°C (feels like {weather['feels_like']}°C)")
            print(f"🌈Min/Max: {weather['temp_min']}°C / {weather['temp_max']}°C")
            print(f"💧Humidity: {weather['humidity']}% | Pressure: {weather['pressure']} hPa")
            print(f"☁️Weather: {weather['weather_main']} - {weather['weather_description'].capitalize()}")
            print(f"🌬️Wind: {weather['wind_speed']} m/s, Direction: {weather['wind_deg']}°")
            print(f"☁️Clouds: {weather['clouds']}% | Visibility: {weather['visibility']} m")
            print(f"🌧️Rain (last 1h): {weather['rain_1h']} mm | Snow (last 1h): {weather['snow_1h']} mm")
            print(f"🌅Sunrise: {format_unix_time(weather['sunrise'])}")
            print(f"🌇Sunset: {format_unix_time(weather['sunset'])}")


