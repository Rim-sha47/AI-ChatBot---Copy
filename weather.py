import requests

def get_weather(city):
    # Using wttr.in which doesn't require an API key and returns plain text
    try:
        # Format: %C for condition, %t for temperature, %h for humidity, %w for wind
        url = f"https://wttr.in/{city}?format=%C,+%t,+Humidity:+%h,+Wind:+%w"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            weather_data = response.text.strip()
            if "Unknown location" in weather_data:
                return f"Could not find weather for '{city}'."
            return f"Weather in {city.title()}: {weather_data}"
        else:
            return f"Failed to get weather data for {city}."
    except requests.RequestException:
        return "Error connecting to the weather service. Please check your internet connection."
