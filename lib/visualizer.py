import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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

def format_closest_miss_table(closest_df):
    """
    format the daily closest miss table for display.

    args:
        closest_df (pandas.DataFrame): dataframe with one asteroid per day (closest miss)

    returns:
        pandas.DataFrame: formatted dataframe for display
    """
    if closest_df is None or len(closest_df) == 0:
        return pd.DataFrame()

    base_columns = ['name', 'diameter_mean_km', 'miss_distance_km', 'relative_velocity_km_s', 'risk_score']
    columns = [c for c in base_columns if c in closest_df.columns]
    if 'risk_level' in closest_df.columns:
        columns.append('risk_level')

    table = closest_df[columns].reset_index()

    if 'date' in table.columns:
        table['date'] = pd.to_datetime(table['date']).dt.date

    if 'diameter_mean_km' in table.columns:
        table['diameter_mean_km'] = table['diameter_mean_km'].round(3)

    if 'miss_distance_km' in table.columns:
        table['miss_distance_km'] = (table['miss_distance_km'] / 1_000_000).round(3).astype(str) + ' million'

    if 'relative_velocity_km_s' in table.columns:
        table['relative_velocity_km_s'] = table['relative_velocity_km_s'].round(2)

    if 'risk_score' in table.columns:
        table['risk_score'] = table['risk_score'].round(4)

    label_map = {
        'date': 'Date',
        'name': 'Name',
        'diameter_mean_km': 'Diameter (km)',
        'miss_distance_km': 'Miss Distance',
        'relative_velocity_km_s': 'Velocity (km/s)',
        'risk_score': 'Risk Score',
        'risk_level': 'Risk Level',
    }
    table = table.rename(columns={k: v for k, v in label_map.items() if k in table.columns})

    return table

def create_risk_calendar_heatmap(df, value_col='avg_risk_score', title='Risk Heatmap Calendar'):
    """
    create a github-style calendar heatmap for a daily metric.

    args:
        df (pandas.DataFrame): daily time series dataframe with a datetime index
        value_col (str): column name to visualize (e.g., 'avg_risk_score')
        title (str): plot title

    returns:
        plotly.graph_objects.Figure: calendar heatmap figure
    """
    if df is None or df.empty or value_col not in df.columns:

        return go.Figure()

    ts = df.copy()

    if not isinstance(ts.index, pd.DatetimeIndex):
        ts.index = pd.to_datetime(ts.get('date', ts.index))

    ts = ts.sort_index()

    ts.index = ts.index.normalize()
    ts[value_col] = ts[value_col].astype(float).fillna(0.0)

    min_date = ts.index.min()
    max_date = ts.index.max()
    grid_start = min_date - pd.to_timedelta(min_date.weekday(), unit='D')  # monday of first week
    grid_end = max_date - pd.to_timedelta(max_date.weekday(), unit='D')    # monday of last week

    week_starts = pd.date_range(grid_start, grid_end, freq='7D')
    weekdays = list(range(0, 7))  # 0=mon

    values_by_date = ts[value_col]

    z_matrix = []
    text_matrix = []
    customdate_matrix = []
    for wd in weekdays:
        row_z = []
        row_text = []
        row_custom = []
        for ws in week_starts:
            current_date = (ws + pd.to_timedelta(wd, unit='D')).normalize()
            value = float(values_by_date.get(current_date, 0.0))
            row_z.append(value)
            row_text.append(str(current_date.day))
            row_custom.append(current_date.strftime('%Y-%m-%d'))
        z_matrix.append(row_z)
        text_matrix.append(row_text)
        customdate_matrix.append(row_custom)

    x_labels = [d.strftime('%b %d') for d in week_starts]
    y_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    fig = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=x_labels,
        y=y_labels,
        colorscale='YlOrRd',
        colorbar=dict(title='Avg Risk'),
        text=text_matrix,
        texttemplate='%{text}',
        textfont={'size': 8},
        hovertemplate='Date: %{customdata}<br>Avg Risk: %{z:.3f}<extra></extra>',
        customdata=customdate_matrix,
        zmin=0,
        zmax=1,
    ))

    fig.update_layout(
        title=title,
        xaxis=dict(title='Week Start', showgrid=False, tickmode='auto', nticks=12),
        yaxis=dict(title='', showgrid=False, autorange='reversed'),
        margin=dict(l=10, r=10, t=60, b=10),
    )

    return fig