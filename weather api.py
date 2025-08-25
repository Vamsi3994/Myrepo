import requests
from datetime import datetime, timedelta


def get_historical_weather(latitude, longitude, days_back=7):
    """
    Retrieves historical weather data for the last 'days_back' days.

    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
        days_back (int): The number of days to look back.

    Returns:
        dict: A dictionary containing the historical weather data, or None on error.
    """

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)

    base_url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "hourly": "temperature_2m",
        "timezone": "auto"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None


def analyze_weather_data(data):
    """
    Analyzes weather data to find highs, lows, and anomalies.

    Args:
        data (dict): The weather data from the API.
    """
    if not data or "hourly" not in data or not data['hourly']['temperature_2m']:
        print("No valid data to analyze.")
        return

    temperatures = data['hourly']['temperature_2m']
    timestamps = data['hourly']['time']

    max_temp = float('-inf')
    min_temp = float('inf')
    max_date = None
    min_date = None

    daily_records = {}

    print("\n--- Weather Records for the Last 7 Days ---")

    for i in range(len(timestamps)):
        timestamp = timestamps[i]
        temp = temperatures[i]

        # Skip if temperature data is missing (represented as None)
        if temp is None:
            continue

        dt_object = datetime.fromisoformat(timestamp)
        date_str = dt_object.strftime("%Y-%m-%d")

        # Initialize daily record if it doesn't exist
        if date_str not in daily_records:
            daily_records[date_str] = {'high': temp, 'low': temp, 'readings': []}

        # Update daily high and low
        daily_records[date_str]['high'] = max(daily_records[date_str]['high'], temp)
        daily_records[date_str]['low'] = min(daily_records[date_str]['low'], temp)
        daily_records[date_str]['readings'].append(temp)

        # Update overall max and min temperatures and their dates
        if temp > max_temp:
            max_temp = temp
            max_date = dt_object

        if temp < min_temp:
            min_temp = temp
            min_date = dt_object

    # Print daily records
    for date, record in sorted(daily_records.items()):
        print(f"Date: {date}")
        print(f"  Highest Daily Temp: {record['high']}°C")
        print(f"  Lowest Daily Temp: {record['low']}°C")

    # Check if data was found
    if max_date and min_date:
        max_day = max_date.strftime("%A")
        min_day = min_date.strftime("%A")

        print("\n--- Temperature Extremes ---")
        print(f"The highest temperature recorded in the last 7 days was {max_temp}°C.")
        print(f"The lowest temperature recorded in the last 7 days was {min_temp}°C.")
        print(f"The date with the highest temperature was {max_date.strftime('%Y-%m-%d')} ({max_day}).")
        print(f"The date with the lowest temperature was {min_date.strftime('%Y-%m-%d')} ({min_day}).")

        print("\n--- Anomalies ---")
        all_temps = [temp for day in daily_records.values() for temp in day['readings']]
        if all_temps:
            average_temp = sum(all_temps) / len(all_temps)
            anomaly_threshold = 10
            anomalies = [
                (timestamps[i], temperatures[i]) for i, temp in enumerate(temperatures)
                if temp is not None and abs(temp - average_temp) > anomaly_threshold
            ]

            if anomalies:
                print("Potential anomalies detected (temperatures deviating by more than 10°C from the average):")
                for timestamp, temp in anomalies:
                    dt_object = datetime.fromisoformat(timestamp)
                    print(f"  - {dt_object.strftime('%Y-%m-%d %H:%M')}: {temp}°C")
            else:
                print("No significant temperature anomalies detected in the last 7 days. 😎")
    else:
        print("\nCould not find temperature extremes.")


# --- Main execution for Hyderabad ---
if __name__ == "__main__":
    # Latitude and Longitude for Hyderabad, India
    lat = 17.3850
    lon = 78.4867

    print(f"Fetching historical weather data for Hyderabad (Lat: {lat}, Lon: {lon})")

    weather_data = get_historical_weather(lat, lon, days_back=7)

    if weather_data:
        analyze_weather_data(weather_data)