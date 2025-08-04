import pandas as pd
import numpy as np
import os

def load_clean_data(filename='asteroids_clean.csv'):
    """
    Load cleaned asteroid data from CSV file.
    
    Args:
        filename (str, optional): Input filename. Defaults to 'asteroids_clean.csv'.
    
    Returns:
        pandas.DataFrame: The loaded asteroid data
    """
    filepath = os.path.join('data', filename)
    if not os.path.exists(filepath):
        print(f"Error: {filepath} does not exist. Please run data_processing.py first.")
        return None
    
    df = pd.read_csv(filepath, parse_dates=['date', 'close_approach_date'])
    df.set_index('date', inplace=True)
    
    print(f"Loaded data from {filepath}")
    return df

def calculate_risk_score(df):
    """
    Calculate risk scores for asteroids based on velocity, size, and miss distance.

    Risk Score Logic:
    - Larger size → more dangerous
    - Higher velocity → more dangerous
    - Closer approach → more dangerous (so smaller distance is worse)

    Returns:
        DataFrame with new 'risk_score' and 'risk_level' columns
    """
    if df is None or df.empty:
        print("Error: Empty DataFrame")
        return None

    scored_df = df.copy()

    diameter_norm = (scored_df['diameter_mean_km'] - scored_df['diameter_mean_km'].min()) / \
                    (scored_df['diameter_mean_km'].max() - scored_df['diameter_mean_km'].min())

    velocity_norm = (scored_df['relative_velocity_km_s'] - scored_df['relative_velocity_km_s'].min()) / \
                    (scored_df['relative_velocity_km_s'].max() - scored_df['relative_velocity_km_s'].min())

    miss_dist_min = scored_df['miss_distance_km'].min()
    miss_dist_max = scored_df['miss_distance_km'].max()
    miss_dist_norm = 1 - ((scored_df['miss_distance_km'] - miss_dist_min) / (miss_dist_max - miss_dist_min))

    # --- COMPOSITE RISK SCORE ---
    # Here's the feature engineering magic:
    # We assign weights to each component and compute a final risk score.
    # - 40% weight to size
    # - 30% to velocity
    # - 30% to miss distance (inverted)
    scored_df['risk_score'] = (0.4 * diameter_norm) + (0.3 * velocity_norm) + (0.3 * miss_dist_norm)

    # --- HAZARDOUS ADJUSTMENT ---
    # This part boosts the risk score by 0.2 if the asteroid is flagged as hazardous by NASA.
    # It's a hard-coded bump — a trust signal to the experts’ warning.
    scored_df.loc[scored_df['is_potentially_hazardous'] == True, 'risk_score'] += 0.2

    scored_df['risk_score'] = scored_df['risk_score'].clip(upper=1.0)

    scored_df['risk_level'] = pd.cut(
        scored_df['risk_score'], 
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
    )

    return scored_df

def calculate_z_scores(df):
    """
    Calculate z-scores for numerical columns to identify anomalies.
    
    Args:
        df (pandas.DataFrame): DataFrame containing asteroid data
    
    Returns:
        pandas.DataFrame: DataFrame with added z-score columns
    """
    if df is None or df.empty:
        print("Error: Empty DataFrame")
        return None
    
    z_df = df.copy()
    
    columns = ['diameter_mean_km', 'miss_distance_km', 'relative_velocity_km_s', 'risk_score']
    
    for col in columns:
        if col in z_df.columns:
            col_mean = z_df[col].mean()
            col_std = z_df[col].std()
            z_df[f'{col}_zscore'] = (z_df[col] - col_mean) / col_std
    
    z_df['is_anomaly'] = False
    for col in columns:
        z_col = f'{col}_zscore'
        if z_col in z_df.columns:
            z_df.loc[abs(z_df[z_col]) > 2, 'is_anomaly'] = True
    
    return z_df

def generate_time_series_data(df):
    """
    Generate time series data for analysis, including rolling averages.
    
    Args:
        df (pandas.DataFrame): DataFrame containing asteroid data
    
    Returns:
        pandas.DataFrame: DataFrame with time series aggregations
    """
    if df is None or df.empty:
        print("Error: Empty DataFrame")
        return None
    
    daily_counts = df.resample('D').size().to_frame('asteroid_count')
    
    daily_avg_diameter = df.resample('D')['diameter_mean_km'].mean().to_frame('avg_diameter_km')
    daily_avg_velocity = df.resample('D')['relative_velocity_km_s'].mean().to_frame('avg_velocity_km_s')
    daily_avg_miss = df.resample('D')['miss_distance_km'].mean().to_frame('avg_miss_distance_km')
    
    if 'risk_score' in df.columns:
        daily_avg_risk = df.resample('D')['risk_score'].mean().to_frame('avg_risk_score')
        daily_high_risk = df[df['risk_score'] > 0.6].resample('D').size().to_frame('high_risk_count')
        
        daily_data = pd.concat([daily_counts, daily_avg_diameter, daily_avg_velocity, 
                              daily_avg_miss, daily_avg_risk, daily_high_risk], axis=1)
    else:
        daily_data = pd.concat([daily_counts, daily_avg_diameter, daily_avg_velocity, daily_avg_miss], axis=1)
    
    count_columns = ['asteroid_count']
    if 'high_risk_count' in daily_data.columns:
        count_columns.append('high_risk_count')
    daily_data[count_columns] = daily_data[count_columns].fillna(0)
    
    for col in daily_data.columns:
        daily_data[f'{col}_7d_avg'] = daily_data[col].rolling(window=7, min_periods=1).mean()
    
    return daily_data

def prepare_visualization_data(df):
    """
    Prepare data subsets for different visualizations.
    
    Args:
        df (pandas.DataFrame): DataFrame containing asteroid data with risk scores
    
    Returns:
        dict: Dictionary containing different data subsets for visualization
    """
    if df is None or df.empty:
        print("Error: Empty DataFrame")
        return None
    
    viz_data = {}
    
    if 'risk_score' in df.columns:
        viz_data['top_risk_asteroids'] = df.sort_values('risk_score', ascending=False).head(10)
    
    viz_data['hazardous_asteroids'] = df[df['is_potentially_hazardous'] == True]
    
    viz_data['large_asteroids'] = df[df['diameter_mean_km'] > 0.5]
    
    viz_data['close_approach'] = df[df['miss_distance_km'] < 10000000]
    
    viz_data['fast_asteroids'] = df[df['relative_velocity_km_s'] > 20]
    
    if 'is_anomaly' in df.columns:
        viz_data['anomalous_asteroids'] = df[df['is_anomaly'] == True]
    
    return viz_data

def analyze_asteroid_data(input_file='asteroids_clean.csv', output_file='asteroids_analyzed.csv'):
    """
    Analyze asteroid data by calculating risk scores, z-scores, and preparing for visualization.
    
    Args:
        input_file (str, optional): Input CSV filename. Defaults to 'asteroids_clean.csv'.
        output_file (str, optional): Output CSV filename. Defaults to 'asteroids_analyzed.csv'.
    
    Returns:
        tuple: (analyzed_df, time_series_df, viz_data_dict)
    """
    df = load_clean_data(input_file)
    if df is None:
        return None, None, None
    
    print("Calculating risk scores...")
    scored_df = calculate_risk_score(df)
    
    print("Calculating z-scores...")
    analyzed_df = calculate_z_scores(scored_df)
    
    print("Generating time series data...")
    time_series_df = generate_time_series_data(analyzed_df)
    
    print("Preparing visualization data...")
    viz_data = prepare_visualization_data(analyzed_df)
    
    filepath = os.path.join('data', output_file)
    analyzed_df.to_csv(filepath)
    print(f"Analyzed data saved to {filepath}")
    
    time_series_filepath = os.path.join('data', 'time_series_data.csv')
    time_series_df.to_csv(time_series_filepath)
    print(f"Time series data saved to {time_series_filepath}")
    
    return analyzed_df, time_series_df, viz_data

if __name__ == "__main__":
    analyzed_df, time_series_df, viz_data = analyze_asteroid_data()
    
    if analyzed_df is not None:
        print("\nAnalysis Summary:")
        print(f"Number of asteroids: {len(analyzed_df)}")
        print(f"Date range: {analyzed_df.index.min().date()} to {analyzed_df.index.max().date()}")
        print(f"Average risk score: {analyzed_df['risk_score'].mean():.4f}")
        print(f"High risk asteroids (score > 0.6): {len(analyzed_df[analyzed_df['risk_score'] > 0.6])}")
        print(f"Anomalous asteroids: {analyzed_df['is_anomaly'].sum()}")
        
        print("\nTop 5 Highest Risk Asteroids:")
        top_5 = analyzed_df.sort_values('risk_score', ascending=False).head(5)
        for idx, row in top_5.iterrows():
            print(f"{row['name']}: Risk Score = {row['risk_score']:.4f}, Diameter = {row['diameter_mean_km']:.2f} km, "  
                  f"Miss Distance = {row['miss_distance_km']/1000000:.2f} million km")