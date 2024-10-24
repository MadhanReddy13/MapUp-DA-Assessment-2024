from typing import Dict, List
import pandas as pd
import itertools
import re
from datetime import datetime, timedelta


def reverse_by_n_elements(lst: List[int], n: int) -> List[int]:
    """
    Reverses the input list by groups of n elements.
    """
    return [item for group in (lst[i:i + n] for i in range(0, len(lst), n)) for item in reversed(group)]


def group_by_length(lst: List[str]) -> Dict[int, List[str]]:
    """
    Groups the strings by their length and returns a dictionary.
    """
    grouped = {}
    for string in lst:
        length = len(string)
        if length not in grouped:
            grouped[length] = []
        grouped[length].append(string)
    return grouped


def flatten_dict(nested_dict: Dict, sep: str = '.') -> Dict:
    """
    Flattens a nested dictionary into a single-level dictionary with dot notation for keys.
    """
    flat_dict = {}

    def flatten(current_dict: Dict, parent_key: str = ''):
        for key, value in current_dict.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                flatten(value, new_key)
            else:
                flat_dict[new_key] = value

    flatten(nested_dict)
    return flat_dict


def unique_permutations(nums: List[int]) -> List[List[int]]:
    """
    Generate all unique permutations of a list that may contain duplicates.
    """
    return list(map(list, set(itertools.permutations(nums))))


def find_all_dates(text: str) -> List[str]:
    """
    This function takes a string as input and returns a list of valid dates
    in 'dd-mm-yyyy', 'mm/dd/yyyy', or 'yyyy.mm.dd' format found in the string.
    """
    date_patterns = [
        r'\b\d{2}-\d{2}-\d{4}\b',    
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',  
        r'\b\d{4}\.\d{1,2}\.\d{1,2}\b'  
    ]
    
    found_dates = []
    for pattern in date_patterns:
        found_dates.extend(re.findall(pattern, text))
    
    valid_dates = []
    for date in found_dates:
        try:
            if '-' in date:
                dt = datetime.strptime(date, '%d-%m-%Y')
            elif '/' in date:
                dt = datetime.strptime(date, '%m/%d/%Y')
            elif '.' in date:
                dt = datetime.strptime(date, '%Y.%m.%d')
            valid_dates.append(dt.strftime('%Y-%m-%d')) 
        except ValueError:
            continue
    
    return valid_dates


def polyline_to_dataframe(polyline_str: str) -> pd.DataFrame:
    """
    Converts a polyline string into a DataFrame with latitude, longitude, and distance between consecutive points.
    """
  
    coords = polyline_str.split(';')
    points = []
    for coord in coords:
        lat, lng = map(float, coord.split(','))
        points.append((lat, lng))

    
    distances = [0]
    for i in range(1, len(points)):
        lat1, lon1 = points[i - 1]
        lat2, lon2 = points[i]
        distance = ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5  
        distances.append(distance)

    df = pd.DataFrame(points, columns=['latitude', 'longitude'])
    df['distance'] = distances
    return df


def rotate_and_multiply_matrix(matrix: List[List[int]]) -> List[List[int]]:
    """
    Rotate the given matrix by 90 degrees clockwise, then multiply each element 
    by the sum of its original row and column index before rotation.
    """
   
    rotated = [list(row) for row in zip(*matrix[::-1])]
    transformed_matrix = []
    for i in range(len(rotated)):
        new_row = []
        for j in range(len(rotated[0])):
            new_value = rotated[i][j] * (i + j)
            new_row.append(new_value)
        transformed_matrix.append(new_row)

    return transformed_matrix


def time_check(df: pd.DataFrame) -> pd.Series:
    """
    Use shared dataset-2 to verify the completeness of the data by checking whether the timestamps for each unique (`id`, `id_2`) pair cover a full 24-hour and 7 days period.
    """
    df['timestamp'] = pd.to_datetime(df['timestamp'])  
    complete_series = df.groupby(['id', 'id_2']).apply(lambda group: 
        (group['timestamp'].min() <= group['timestamp'].min() + timedelta(days=7)) and 
        (group['timestamp'].max() >= group['timestamp'].min() + timedelta(days=1))
    )
    
    return complete_series
