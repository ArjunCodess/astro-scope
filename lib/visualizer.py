import plotly.express as px

def create_time_series_plot(df, columns, title, y_label='Value'):
    """
    Create a time series line plot.
    
    Args:
        df (pandas.DataFrame): Time series DataFrame
        columns (list): List of columns to plot
        title (str): Plot title
        y_label (str): Y-axis label
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    fig = px.line(
        df, 
        y=columns,
        labels={'value': y_label, 'variable': 'Metric'},
        title=title
    )
    return fig

def create_risk_histogram(df, title='Distribution of Risk Scores'):
    """
    Create a histogram of risk scores.
    
    Args:
        df (pandas.DataFrame): DataFrame with risk_score column
        title (str): Plot title
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    fig = px.histogram(
        df, 
        x='risk_score',
        nbins=20,
        title=title
    )
    return fig

def create_risk_level_pie(df, title='Risk Level Distribution'):
    """
    Create a pie chart of risk levels.
    
    Args:
        df (pandas.DataFrame): DataFrame with risk_level column
        title (str): Plot title
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    risk_level_counts = df['risk_level'].value_counts()
    fig = px.pie(
        values=risk_level_counts.values,
        names=risk_level_counts.index,
        title=title
    )
    return fig

def create_scatter_plot(df, title='Miss Distance vs. Velocity'):
    """
    Create a scatter plot of miss distance vs velocity with risk coloring.
    
    Args:
        df (pandas.DataFrame): DataFrame with asteroid data
        title (str): Plot title
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    fig = px.scatter(
        df,
        x='miss_distance_km',
        y='relative_velocity_km_s',
        color='risk_score',
        size='diameter_mean_km',
        hover_name='name',
        color_continuous_scale='Viridis',
        title=title,
        labels={
            'miss_distance_km': 'Miss Distance (km)',
            'relative_velocity_km_s': 'Relative Velocity (km/s)',
            'risk_score': 'Risk Score',
            'diameter_mean_km': 'Diameter (km)'
        }
    )
    return fig

def create_diameter_histogram(df, title='Distribution of Asteroid Sizes'):
    """
    Create a histogram of asteroid diameters.
    
    Args:
        df (pandas.DataFrame): DataFrame with diameter_mean_km column
        title (str): Plot title
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    fig = px.histogram(
        df, 
        x='diameter_mean_km',
        nbins=30,
        title=title
    )
    return fig

def format_top_risk_table(top_risk):
    """
    Format the top risk asteroids table for display.
    
    Args:
        top_risk (pandas.DataFrame): DataFrame with top risk asteroids
        
    Returns:
        pandas.DataFrame: Formatted DataFrame for display
    """
    top_risk_table = top_risk[['name', 'diameter_mean_km', 'miss_distance_km', 
                              'relative_velocity_km_s', 'risk_score', 'risk_level']].reset_index()
    
    top_risk_table['date'] = top_risk_table['date'].dt.date
    top_risk_table['diameter_mean_km'] = top_risk_table['diameter_mean_km'].round(3)
    top_risk_table['miss_distance_km'] = (top_risk_table['miss_distance_km'] / 1000000).round(3).astype(str) + ' million'
    top_risk_table['relative_velocity_km_s'] = top_risk_table['relative_velocity_km_s'].round(2)
    top_risk_table['risk_score'] = top_risk_table['risk_score'].round(4)
    
    top_risk_table.columns = ['Date', 'Name', 'Diameter (km)', 'Miss Distance', 
                             'Velocity (km/s)', 'Risk Score', 'Risk Level']
    
    return top_risk_table

def format_anomalous_table(anomalous):
    """
    Format the anomalous asteroids table for display.
    
    Args:
        anomalous (pandas.DataFrame): DataFrame with anomalous asteroids
        
    Returns:
        pandas.DataFrame: Formatted DataFrame for display
    """
    if len(anomalous) == 0:
        return None
        
    anomalous_table = anomalous[['name', 'diameter_mean_km', 'miss_distance_km', 
                               'relative_velocity_km_s', 'risk_score']].reset_index()
    
    anomalous_table['date'] = anomalous_table['date'].dt.date
    anomalous_table['diameter_mean_km'] = anomalous_table['diameter_mean_km'].round(3)
    anomalous_table['miss_distance_km'] = (anomalous_table['miss_distance_km'] / 1000000).round(3).astype(str) + ' million'
    anomalous_table['relative_velocity_km_s'] = anomalous_table['relative_velocity_km_s'].round(2)
    anomalous_table['risk_score'] = anomalous_table['risk_score'].round(4)
    
    anomalous_table.columns = ['Date', 'Name', 'Diameter (km)', 'Miss Distance', 
                              'Velocity (km/s)', 'Risk Score']
    
    return anomalous_table