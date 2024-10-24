import pandas as pd
import numpy as np

def calculate_distance_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate a distance matrix based on the dataframe, df.
    
    Args:
        df (pandas.DataFrame): DataFrame with 'id', 'latitude', 'longitude'.
        
    Returns:
        pandas.DataFrame: Distance matrix
    """
   
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat / 2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return R * c * 1000 
    ids = df['id'].unique()
    distance_matrix = pd.DataFrame(index=ids, columns=ids)

    for i in range(len(df)):
        for j in range(len(df)):
            if i != j:
                distance = haversine(df.iloc[i]['latitude'], df.iloc[i]['longitude'],
                                     df.iloc[j]['latitude'], df.iloc[j]['longitude'])
                distance_matrix.iloc[i, j] = distance
            else:
                distance_matrix.iloc[i, j] = 0

    return distance_matrix

def unroll_distance_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.
    
    Args:
        df (pandas.DataFrame): Distance matrix with IDs as both index and columns.
        
    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    unrolled = []
    
    for start_id in df.index:
        for end_id in df.columns:
            unrolled.append({'id_start': start_id, 'id_end': end_id, 'distance': df.loc[start_id, end_id]})
    
    return pd.DataFrame(unrolled)

def find_ids_within_ten_percentage_threshold(df: pd.DataFrame, reference_id: int) -> pd.DataFrame:
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.
    
    Args:
        df (pandas.DataFrame): Unrolled DataFrame containing 'id_start', 'id_end', and 'distance'.
        reference_id (int): The reference ID for calculating the threshold.
        
    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    reference_avg = df[df['id_start'] == reference_id]['distance'].mean()
    lower_bound = reference_avg * 0.9
    upper_bound = reference_avg * 1.1
    avg_distances = df.groupby('id_start')['distance'].mean()
    within_threshold = avg_distances[(avg_distances >= lower_bound) & (avg_distances <= upper_bound)]
    
    return within_threshold.reset_index()

def calculate_toll_rate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.
    
    Args:
        df (pandas.DataFrame): Unrolled DataFrame with vehicle types.
        
    Returns:
        pandas.DataFrame: DataFrame with toll rates for each vehicle type.
    """
  
    toll_rates = {
        'car': 1.0,
        'truck': 1.5,
        'bus': 1.2
    }

    df['vehicle_type'] = df['id_start'].map(toll_rates) 
    df['toll_rate'] = df['distance'] * df['vehicle_type']
    
    return df[['id_start', 'id_end', 'toll_rate']]

def calculate_time_based_toll_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate time-based toll rates for different time intervals within a day.
    
    Args:
        df (pandas.DataFrame): DataFrame containing timestamps and distances.
        
    Returns:
        pandas.DataFrame: DataFrame with time-based toll rates.
    """
    time_based_rates = {
        '00:00': 0.5,
        '06:00': 1.0,
        '12:00': 1.5,
        '18:00': 2.0,
        '23:59': 1.0
    }

    df['time'] = pd.to_datetime(df['timestamp']).dt.time
    df['toll_rate'] = df['time'].apply(lambda x: next((rate for time, rate in time_based_rates.items() if x >= pd.to_datetime(time).time()), 1.0))
    
    return df[['id_start', 'id_end', 'toll_rate']]
