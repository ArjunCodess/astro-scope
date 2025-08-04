import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv()

data_dir = os.getenv('DATA_DIR', 'data')

def load_raw_data(filename='asteroids_raw.json'):
    """
    Load raw asteroid data from JSON file.
    
    Args:
        filename (str, optional): Input filename. Defaults to 'asteroids_raw.json'.
    
    Returns:
        dict: The loaded asteroid data
    """
    filepath = os.path.join(data_dir, filename)
    if not os.path.exists(filepath):
        print(f"Error: {filepath} does not exist. Please run data_fetcher.py first.")
        return None
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    print(f"Loaded data from {filepath}")
    return data

def flatten_asteroid_data(data):
    """
    Flatten the nested JSON structure of asteroid data into a list of dictionaries.
    
    Args:
        data (dict): Raw asteroid data from NASA NeoWs API
    
    Returns:
        list: Flattened list of asteroid dictionaries
    """
    if not data or 'near_earth_objects' not in data:
        print("Error: Invalid data format")
        return []
    
    flattened_data = []
    
    for date, asteroids in data['near_earth_objects'].items():
        for asteroid in asteroids:
            asteroid_info = {
                'date': date,
                'id': asteroid.get('id'),
                'name': asteroid.get('name'),
                'is_potentially_hazardous': asteroid.get('is_potentially_hazardous_asteroid', False)
            }
            
            if 'estimated_diameter' in asteroid and 'kilometers' in asteroid['estimated_diameter']:
                asteroid_info['diameter_min_km'] = asteroid['estimated_diameter']['kilometers'].get('estimated_diameter_min')
                asteroid_info['diameter_max_km'] = asteroid['estimated_diameter']['kilometers'].get('estimated_diameter_max')
                asteroid_info['diameter_mean_km'] = (asteroid_info['diameter_min_km'] + asteroid_info['diameter_max_km']) / 2 if asteroid_info['diameter_min_km'] and asteroid_info['diameter_max_km'] else None
            
            if 'close_approach_data' in asteroid and asteroid['close_approach_data']:
                approach = asteroid['close_approach_data'][0]
                
                if 'miss_distance' in approach:
                    asteroid_info['miss_distance_km'] = float(approach['miss_distance'].get('kilometers', 0))
                
                if 'relative_velocity' in approach:
                    asteroid_info['relative_velocity_km_h'] = float(approach['relative_velocity'].get('kilometers_per_hour', 0))
                    asteroid_info['relative_velocity_km_s'] = asteroid_info['relative_velocity_km_h'] / 3600
                
                asteroid_info['close_approach_date'] = approach.get('close_approach_date')
            
            flattened_data.append(asteroid_info)
    
    return flattened_data

def create_dataframe(flattened_data):
    """
    Create a pandas DataFrame from flattened asteroid data.
    
    Args:
        flattened_data (list): Flattened list of asteroid dictionaries
    
    Returns:
        pandas.DataFrame: DataFrame containing asteroid data
    """
    if not flattened_data:
        print("Error: No data to create DataFrame")
        return None
    
    df = pd.DataFrame(flattened_data)
    
    date_columns = ['date', 'close_approach_date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    if 'date' in df.columns:
        df.set_index('date', inplace=True)
    
    return df

def clean_dataframe(df):
    """
    Clean the DataFrame by handling missing values and data type conversions.
    
    Args:
        df (pandas.DataFrame): DataFrame to clean
    
    Returns:
        pandas.DataFrame: Cleaned DataFrame
    """
    if df is None or df.empty:
        print("Error: Empty DataFrame")
        return None
    
    cleaned_df = df.copy()
    
    numeric_columns = ['diameter_min_km', 'diameter_max_km', 'diameter_mean_km', 
                      'miss_distance_km', 'relative_velocity_km_h', 'relative_velocity_km_s']
    
    for col in numeric_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
            median_value = cleaned_df[col].median()
            cleaned_df.loc[:, col] = cleaned_df[col].fillna(median_value)
    
    bool_columns = ['is_potentially_hazardous']
    for col in bool_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].astype(bool)
    
    return cleaned_df

def save_clean_data(df, filename='asteroids_clean.csv'):
    """
    Save cleaned DataFrame to CSV file.
    
    Args:
        df (pandas.DataFrame): DataFrame to save
        filename (str, optional): Output filename. Defaults to 'asteroids_clean.csv'.
    """
    if df is None or df.empty:
        print("Error: No data to save")
        return
    
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath)
    print(f"Cleaned data saved to {filepath}")

def process_asteroid_data(input_file='asteroids_raw.json', output_file='asteroids_clean.csv'):
    """
    Process asteroid data from raw JSON to cleaned CSV.
    
    Args:
        input_file (str, optional): Input JSON filename. Defaults to 'asteroids_raw.json'.
        output_file (str, optional): Output CSV filename. Defaults to 'asteroids_clean.csv'.
    
    Returns:
        pandas.DataFrame: Cleaned DataFrame
    """
    raw_data = load_raw_data(input_file)
    if not raw_data:
        return None
    
    print("Flattening asteroid data...")
    flattened_data = flatten_asteroid_data(raw_data)
    
    print("Creating DataFrame...")
    df = create_dataframe(flattened_data)
    
    print("Cleaning data...")
    cleaned_df = clean_dataframe(df)
    
    save_clean_data(cleaned_df, output_file)
    
    return cleaned_df

if __name__ == "__main__":
    df = process_asteroid_data()
    
    if df is not None:
        print("\nDataset Statistics:")
        print(f"Number of asteroids: {len(df)}")
        print(f"Date range: {df.index.min().date()} to {df.index.max().date()}")
        print(f"Average diameter: {df['diameter_mean_km'].mean():.2f} km")
        print(f"Average miss distance: {df['miss_distance_km'].mean():.2f} km")
        print(f"Potentially hazardous asteroids: {df['is_potentially_hazardous'].sum()} ({df['is_potentially_hazardous'].mean()*100:.1f}%)")