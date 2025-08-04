import streamlit as st
import pandas as pd
import os
from datetime import datetime
from lib import visualizer

st.set_page_config(
    page_title="AstroScope: NASA Asteroid Dashboard",
    page_icon="🔭",
    layout="wide"
)

def load_data():
    """Load the analyzed asteroid data and time series data"""
    analyzed_path = os.path.join('data', 'asteroids_analyzed.csv')
    time_series_path = os.path.join('data', 'time_series_data.csv')
    
    if not os.path.exists(analyzed_path) or not os.path.exists(time_series_path):
        st.error("Data files not found. Please run the analysis.py script first.")
        return None, None
    
    analyzed_df = pd.read_csv(analyzed_path, parse_dates=['date', 'close_approach_date'])
    analyzed_df.set_index('date', inplace=True)
    
    time_series_df = pd.read_csv(time_series_path, parse_dates=['date'])
    time_series_df.set_index('date', inplace=True)
    
    return analyzed_df, time_series_df

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
    st.title("🔭 AstroScope: NASA Asteroid Dashboard")
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
    risk_threshold = st.sidebar.slider(
        "Risk Score Threshold",
        0.0, 1.0, 0.5, 0.05
    )
    
    # Filter data based on date range
    filtered_df = analyzed_df.loc[start_date:end_date]
    
    # Dashboard metrics
    st.header("Dashboard Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Asteroids", len(filtered_df))
    
    with col2:
        high_risk_count = len(filtered_df[filtered_df['risk_score'] > risk_threshold])
        st.metric("High Risk Asteroids", high_risk_count)
    
    with col3:
        avg_diameter = filtered_df['diameter_mean_km'].mean()
        st.metric("Avg. Diameter (km)", f"{avg_diameter:.2f}")
    
    with col4:
        hazardous_count = filtered_df['is_potentially_hazardous'].sum()
        st.metric("Potentially Hazardous", hazardous_count)
    
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
    
    st.header("Additional Insights")
    
    tab1, tab2 = st.tabs(["Size Distribution", "Anomalous Asteroids"])
    
    with tab1:
        fig = visualizer.create_diameter_histogram(filtered_df)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        anomalous = filtered_df[filtered_df['is_anomaly'] == True]
        anomalous_table = visualizer.format_anomalous_table(anomalous)
        
        if anomalous_table is not None:
            st.dataframe(anomalous_table, use_container_width=True)
        else:
            st.info("No anomalous asteroids found in the selected date range.")

    st.markdown("---")
    st.markdown("""
    **AstroScope: NASA Asteroid Dashboard** | Data from NASA NeoWs API | Last updated: {}
    """.format(datetime.now().strftime("%Y-%m-%d")))

if __name__ == "__main__":
    main()