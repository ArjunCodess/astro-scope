import requests
import json
import os
import datetime
import time
from dotenv import load_dotenv

load_dotenv()

data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

def get_nasa_api_key():
    """
    Get NASA API key from environment variable or use DEMO_KEY as fallback.
    
    Returns:
        str: NASA API key
    """
    return os.getenv('NASA_API_KEY')

def fetch_asteroid_data(start_date, end_date, api_key=None):
    """
    Fetch asteroid data from NASA NeoWs API for a given date range.
    
    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        api_key (str, optional): NASA API key. Defaults to None.
    
    Returns:
        dict: JSON response from the API
    """
    if api_key is None:
        api_key = get_nasa_api_key()
    
    url = "https://api.nasa.gov/neo/rest/v1/feed"
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'api_key': api_key
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def fetch_data_in_chunks(start_date, end_date, chunk_size=7, api_key=None):
    """
    Fetch asteroid data in chunks due to API limitations (7 days max per request).
    
    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        chunk_size (int, optional): Size of each chunk in days. Defaults to 7.
        api_key (str, optional): NASA API key. Defaults to None.
    
    Returns:
        dict: Combined data from all chunks
    """
    if api_key is None:
        api_key = get_nasa_api_key()
    
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    
    all_data = {"near_earth_objects": {}}
    
    current_start = start
    while current_start <= end:
        current_end = current_start + datetime.timedelta(days=min(chunk_size-1, (end-current_start).days))
        
        chunk_start_str = current_start.strftime('%Y-%m-%d')
        chunk_end_str = current_end.strftime('%Y-%m-%d')
        
        print(f"Fetching data from {chunk_start_str} to {chunk_end_str}...")
        
        chunk_data = fetch_asteroid_data(chunk_start_str, chunk_end_str, api_key)
        
        if chunk_data and 'near_earth_objects' in chunk_data:
            all_data['near_earth_objects'].update(chunk_data['near_earth_objects'])
            
            if current_start == start:
                for key, value in chunk_data.items():
                    if key != 'near_earth_objects':
                        all_data[key] = value
        
        current_start = current_end + datetime.timedelta(days=1)
        
        time.sleep(1)
    
    return all_data

def save_data_to_json(data, filename='asteroids_raw.json'):
    """
    Save asteroid data to a JSON file.
    
    Args:
        data (dict): Asteroid data to save
        filename (str, optional): Output filename. Defaults to 'asteroids_raw.json'.
    """
    filepath = os.path.join('data', filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filepath}")

def fetch_and_save_asteroid_data(days=90, api_key=None):
    """
    Fetch asteroid data for the last N days and save it to a file.
    
    Args:
        days (int, optional): Number of days to fetch data for. Defaults to 90.
        api_key (str, optional): NASA API key. Defaults to None.
    
    Returns:
        dict: The fetched asteroid data
    """
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    print(f"Fetching asteroid data for the last {days} days ({start_date_str} to {end_date_str})...")
    
    data = fetch_data_in_chunks(start_date_str, end_date_str, api_key=api_key)
    
    if data:
        save_data_to_json(data)
        return data
    else:
        print("Failed to fetch asteroid data.")
        return None

if __name__ == "__main__":
    api_key = get_nasa_api_key()
    print(f"Using API key: {api_key}")
    
    fetch_and_save_asteroid_data(days=30, api_key=api_key)