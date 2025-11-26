#!/usr/bin/env python3

import pandas as pd

#================ Label mapping and counts =====================
def mapping_from_dict(column_name, data_dict):
    """
    Retrieves the code to textual label mapping for a given column from the data dictionary.
    
    Args:
        column_name (str): The column key (e.g, 'SEX').
        data_dict (dict): The loaded JSON data dictionary.
        
    Returns:
        dict: A dictionary mapping code string (e.g, "1") to label string (e.g, "Female").
    """
    # .get() to retrieve the dictionary associated with the column name
    return data_dict.get(column_name, {})

def get_labels_and_counts(df, column_name, code_mapping):
    """
    Calculates value counts and prepares descriptive labels .

    Args:
        df: The input DataFrame.
        column_name (str): The column to analyse.
        code_mapping (dict): The dictionary mapping codes to textual labels.
        
    Returns:
        tuple: (list of textual labels, list of counts)
    """
    # Calculate the raw value counts, sorted by code
    counts = df[column_name].value_counts().sort_index()
    
    codes = counts.index.tolist()
    counts_list = counts.values.tolist()
    labels = []
    
    for code in codes:
        code_str = str(code)
        # Use the data dictionary to get the descriptive text
        label = code_mapping.get(code_str, f"Code {code_str}")
        
        labels.append(label)
        
    return labels, counts_list

#================= 2D tables =================================
def crosstab_groupby(df, col1, col2, data_dict):
    """
    Creates a cross-tabulation table with descriptive labels using pandas groupby().

    Args:
        df: Data from the refined datafram loaded in.
        col1(str): The first column key.
        col2(str): The second column key.
        data_dict(dict): The loaded JSON data dictionary.

    Returns:
        crosstab_df : The cross tabulate data in a dataframe.
    
    """
    
    # code-to-label maps
    map1 = mapping_from_dict(col1, data_dict)
    map2 = mapping_from_dict(col2, data_dict)
    
    # Temporary DataFrame with descriptive labels
    # .astype(str) to ensure codes are matched correctly
    df_temp = pd.DataFrame({
        'Col1': df[col1].astype(str).map(map1),
        'Col2': df[col2].astype(str).map(map2)})
    
    # Create the cross-tabulation using groupby().size().unstack()
    # fill_value=0 ensures that combinations with zero occurrences are represented as 0
    crosstab_df = df_temp.groupby(['Col1', 'Col2']).size().unstack(fill_value=0)
    
    # Clean the index and column names
    crosstab_df.index.name = col1
    crosstab_df.columns.name = col2
    
    return crosstab_df