import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
from lib import visualizer
import io
import zipfile

load_dotenv()

st.set_page_config(
    page_title="AstroScope: NASA Asteroid Dashboard",
    page_icon="./assets/logo.png",
    layout="wide"
)

def load_data():
    """Load the analyzed asteroid data and time series data"""
    data_dir = os.getenv('DATA_DIR', 'data')
    analyzed_path = os.path.join(data_dir, 'asteroids_analyzed.csv')
    time_series_path = os.path.join(data_dir, 'time_series_data.csv')
    
    if not os.path.exists(analyzed_path) or not os.path.exists(time_series_path):
        with st.spinner('Fetching and processing asteroid data...'):
            from lib.data_fetcher import fetch_and_save_asteroid_data
            from lib.data_processing import process_asteroid_data
            from lib.analysis import analyze_asteroid_data
            
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Step 1: Fetch data
            st.info('Fetching asteroid data from NASA API...')
            raw_data = fetch_and_save_asteroid_data()
            if raw_data is None:
                st.error('Failed to fetch asteroid data. Please check your NASA API key in .env file.')
                return None, None
            
            # Step 2: Process data
            st.info('Processing asteroid data...')
            cleaned_df = process_asteroid_data()
            if cleaned_df is None:
                st.error('Failed to process asteroid data.')
                return None, None
            
            # Step 3: Analyze data
            st.info('Analyzing asteroid data...')
            analyzed_df, time_series_df, _ = analyze_asteroid_data()
            if analyzed_df is None:
                st.error('Failed to analyze asteroid data.')
                return None, None
            
            st.success('Data pipeline completed successfully!')
    else:
        analyzed_df = pd.read_csv(analyzed_path, parse_dates=['date', 'close_approach_date'])
        analyzed_df.set_index('date', inplace=True)
        
        time_series_df = pd.read_csv(time_series_path, parse_dates=['date'])
        time_series_df.set_index('date', inplace=True)
    
    return analyzed_df, time_series_df

def create_data_zip(data_dir: str) -> bytes:
    """zip the entire data directory and return bytes"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(data_dir):
            for name in files:
                file_path = os.path.join(root, name)
                arcname = os.path.relpath(file_path, start=data_dir)
                zipf.write(file_path, arcname=arcname)
    buffer.seek(0)
    return buffer.read()

def prepare_viz_data(df):
    """Prepare data subsets for different visualizations"""
    viz_data = {}
    
    viz_data['top_risk_asteroids'] = df.sort_values('risk_score', ascending=False).head(10)
    viz_data['hazardous_asteroids'] = df[df['is_potentially_hazardous'] == True]
    viz_data['large_asteroids'] = df[df['diameter_mean_km'] > 0.5]
    viz_data['close_approach'] = df[df['miss_distance_km'] < 10000000]
    viz_data['fast_asteroids'] = df[df['relative_velocity_km_s'] > 20]
    viz_data['anomalous_asteroids'] = df[df['is_anomaly'] == True]
    
    return viz_data

def main():
    st.image("assets/logo.png", width=100)
    st.title("AstroScope: NASA Asteroid Dashboard")
        
    st.markdown("""
    This dashboard visualizes near-Earth asteroid data from NASA's NeoWs API, 
    providing insights into asteroid sizes, velocities, miss distances, and potential hazards.
    """)
    
    analyzed_df, time_series_df = load_data()
    
    if analyzed_df is None or time_series_df is None:
        return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    min_date = analyzed_df.index.min().date()
    max_date = analyzed_df.index.max().date()
    
    start_date = st.sidebar.date_input(
        "Start Date",
        min_date,
        min_value=min_date,
        max_value=max_date
    )
    
    end_date = st.sidebar.date_input(
        "End Date",
        max_date,
        min_value=start_date,
        max_value=max_date
    )
    
    # Risk threshold filter
    default_threshold = float(os.getenv('RISK_THRESHOLD', 0.6))
    risk_threshold = st.sidebar.slider(
        "Risk Score Threshold",
        0.0, 1.0, default_threshold, 0.05
    )
    
    # Filter data based on date range
    filtered_df = analyzed_df.loc[start_date:end_date]
    
    st.sidebar.divider()
    st.sidebar.header("Custom Alerts")
    alert_type = st.sidebar.radio(
        "Alert Type",
        ["Risk Score", "Z-Score"]
    )
    
    if alert_type == "Risk Score":
        alert_threshold = st.sidebar.slider(
            "Alert Threshold (Risk Score)",
            0.0, 1.0, 0.7, 0.05
        )
        alert_df = filtered_df[filtered_df['risk_score'] > alert_threshold]
        if len(alert_df) > 0:
            st.sidebar.success(f"Found {len(alert_df)} asteroids above risk threshold")
    else:  # Z-Score
        z_score_column = st.sidebar.selectbox(
            "Z-Score Metric",
            ["diameter_mean_km_zscore", "miss_distance_km_zscore", "relative_velocity_km_s_zscore", "risk_score_zscore"]
        )
        z_score_threshold = st.sidebar.slider(
            "Alert Threshold (Z-Score)",
            0.0, 5.0, 2.0, 0.1
        )
        alert_df = filtered_df[filtered_df[z_score_column].abs() > z_score_threshold]
        if len(alert_df) > 0:
            st.sidebar.success(f"Found {len(alert_df)} asteroids above z-score threshold")

    st.sidebar.divider()
    st.sidebar.header("Export Data")
    data_dir = os.getenv('DATA_DIR', 'data')

    files_to_export = [
        ("asteroids_analyzed.csv", "text/csv"),
        ("asteroids_clean.csv", "text/csv"),
        ("asteroids_raw.json", "application/json"),
        ("time_series_data.csv", "text/csv"),
    ]

    any_file_exists = False
    for filename, mime in files_to_export:
        path = os.path.join(data_dir, filename)
        if os.path.exists(path):
            any_file_exists = True
            with open(path, 'rb') as f:
                st.sidebar.download_button(
                    label=f"Download {filename}",
                    data=f.read(),
                    file_name=filename,
                    mime=mime,
                    use_container_width=True,
                )

    if os.path.exists(data_dir) and any_file_exists:
        zip_bytes = create_data_zip(data_dir)
        st.sidebar.download_button(
            label="Download data folder (zip)",
            data=zip_bytes,
            file_name="data.zip",
            mime="application/zip",
            use_container_width=True,
        )
    
    # Dashboard metrics
    st.header("Dashboard Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Asteroids", len(filtered_df))
    
    with col2:
        high_risk_count = len(filtered_df[filtered_df['risk_score'] > risk_threshold])
        st.metric("High Risk Asteroids", high_risk_count)
        if high_risk_count > 0:
            st.toast(f"⚠️ {high_risk_count} high risk asteroids detected!", icon="⚠️")
    
    with col3:
        avg_diameter = filtered_df['diameter_mean_km'].mean()
        st.metric("Avg. Diameter (km)", f"{avg_diameter:.2f}")
    
    with col4:
        hazardous_count = filtered_df['is_potentially_hazardous'].sum()
        st.metric("Potentially Hazardous", hazardous_count)
        if hazardous_count > 0:
            st.toast(f"⚠️ {hazardous_count} potentially hazardous asteroids detected!", icon="⚠️")
    
    # Time series visualizations
    st.header("Time Series Analysis")
    
    filtered_ts = time_series_df.loc[start_date:end_date]
    
    tab1, tab2, tab3 = st.tabs(["Asteroid Count", "Risk Score", "Size & Velocity"])
    
    with tab1:
        # Asteroid count over time
        fig = visualizer.create_time_series_plot(
            filtered_ts, 
            ['asteroid_count', 'asteroid_count_7d_avg'],
            'Asteroid Count Over Time',
            'Count'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Risk score over time
        fig = visualizer.create_time_series_plot(
            filtered_ts, 
            ['avg_risk_score', 'avg_risk_score_7d_avg', 'high_risk_count'],
            'Risk Metrics Over Time'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Size and velocity over time
        fig = visualizer.create_time_series_plot(
            filtered_ts, 
            ['avg_diameter_km', 'avg_velocity_km_s'],
            'Average Size and Velocity Over Time'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk Heatmap Calendar
    st.header("Risk Heatmap Calendar")
    heatmap_fig = visualizer.create_risk_calendar_heatmap(
        filtered_ts, value_col='avg_risk_score', title='Risk Heatmap Calendar'
    )
    st.plotly_chart(heatmap_fig, use_container_width=True)

    # Risk distribution
    st.header("Risk Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram of risk scores
        fig = visualizer.create_risk_histogram(filtered_df)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Pie chart of risk levels
        fig = visualizer.create_risk_level_pie(filtered_df)
        st.plotly_chart(fig, use_container_width=True)
    
    # Scatter plot
    st.header("Asteroid Characteristics")
    
    fig = visualizer.create_scatter_plot(
        filtered_df,
        'Miss Distance vs. Velocity (colored by risk, sized by diameter)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Top 10 risky asteroids
    st.header("Top 10 Highest Risk Asteroids")
    
    top_risk = filtered_df.sort_values('risk_score', ascending=False).head(10)
    
    top_risk_table = visualizer.format_top_risk_table(top_risk)
    st.dataframe(top_risk_table, use_container_width=True)
    
    if len(top_risk) > 0 and top_risk['risk_score'].max() > 0.8:
        st.warning(f"⚠️ High risk asteroid detected: {top_risk.iloc[0]['name']} with risk score {top_risk['risk_score'].max():.2f}")
    
    # Daily Closest Miss (Top 10 by closest approach distance)
    st.header("Daily Closest Miss (Top 10 Dates)")

    if 'miss_distance_km' in filtered_df.columns and not filtered_df.empty:
        closest_idx_per_day = filtered_df.groupby(filtered_df.index.normalize())['miss_distance_km'].idxmin()
        daily_closest = filtered_df.loc[closest_idx_per_day]
        top10_closest = daily_closest.sort_values('miss_distance_km', ascending=True).head(10)

        closest_table = visualizer.format_closest_miss_table(top10_closest)
        st.dataframe(closest_table, use_container_width=True)
    else:
        st.info("closest miss data is unavailable for the selected date range.")

    # Custom Alerts Panel - Display alerts
    st.header(f"Custom Alerts: {alert_type}")
    
    if len(alert_df) > 0:
        if alert_type == "Risk Score":
            st.success(f"Found {len(alert_df)} asteroids with risk score above {alert_threshold}")
            alert_table = visualizer.format_top_risk_table(alert_df)
        else:  # Z-Score
            metric_name = z_score_column.replace('_zscore', '')
            st.success(f"Found {len(alert_df)} asteroids with {metric_name} z-score above {z_score_threshold}")
            
            alert_table = alert_df[['name', 'diameter_mean_km', 'miss_distance_km', 
                                  'relative_velocity_km_s', 'risk_score', z_score_column]].reset_index()
            
            alert_table['date'] = alert_table['date'].dt.date
            alert_table['diameter_mean_km'] = alert_table['diameter_mean_km'].round(3)
            alert_table['miss_distance_km'] = (alert_table['miss_distance_km'] / 1000000).round(3).astype(str) + ' million'
            alert_table['relative_velocity_km_s'] = alert_table['relative_velocity_km_s'].round(2)
            alert_table['risk_score'] = alert_table['risk_score'].round(4)
            alert_table[z_score_column] = alert_table[z_score_column].round(2)
            
            column_names = {
                'date': 'Date',
                'name': 'Name',
                'diameter_mean_km': 'Diameter (km)',
                'miss_distance_km': 'Miss Distance',
                'relative_velocity_km_s': 'Velocity (km/s)',
                'risk_score': 'Risk Score',
                z_score_column: f'{metric_name} Z-Score'
            }
            
            alert_table.rename(columns=column_names, inplace=True)
        
        st.dataframe(alert_table, use_container_width=True)
        st.toast(f"Alert panel updated with {len(alert_df)} asteroids", icon="🚨")
    else:
        st.info(f"No asteroids found above the {alert_type.lower()} threshold.")
    
    st.header("Additional Insights")
    
    tab1, tab2 = st.tabs(["Size Distribution", "Anomalous Asteroids"])
    
    with tab1:
        fig = visualizer.create_diameter_histogram(filtered_df)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        anomalous = filtered_df[filtered_df['is_anomaly'] == True]
        anomalous_table = visualizer.format_anomalous_table(anomalous)
        
        if anomalous_table is not None:
            st.success(f"Found {len(anomalous)} anomalous asteroids")
            st.dataframe(anomalous_table, use_container_width=True)
            st.toast(f"⚠️ {len(anomalous)} anomalous asteroids detected", icon="🔍")
        else:
            st.info("No anomalous asteroids found in the selected date range.")

    st.divider()
    st.markdown("""
    **AstroScope: NASA Asteroid Dashboard** | Data from NASA NeoWs API
    """)

if __name__ == "__main__":
    main()