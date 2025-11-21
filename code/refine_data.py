#!/usr/bin/env python3

import pandas as pd
import json
import argparse
import sys

#============ Loading data and dictionary ======================
def load_data(csv_path):
    """Loads the CSV data into a pandas DataFrame.
    Args:
        csv_path: Path to the required data.

    Returns:
        df: data from the csv loaded into a dataframe.
    """
    print(f"Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Successfully loaded {len(df)} records.")
    print(df.info())                            # can check for missing values and the types in each column
    return df

def load_dictionary(dict_path):
    """Load the data dictionary containing expected variable types and allowed values.
    Args:
        dict_path: Path to the dictionary coontaining labels.
    """
    print(f"Loading data dictionary: {dict_path}")
    with open(dict_path, "r") as f:
        return json.load(f)
    
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

#================= Refine function================================
def refine(df_raw, data_dict):
    """ 
    Performs consistency checks and refines the raw census data:
    - validate types and admissible values using a data dictionary
    - removes duplicates
    
    Args:
        df_raw: data frame with the required data in.
        data_dict: data from the dictionary (codes and labels)

    Returns:
        df_refined: refined data in data frame.
    """
    # catch errors without modifying the original
    df = df_raw.copy()

    # Ensure all required columns exist to start
    expected_cols = list(data_dict.keys())
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing expected columns in raw data: {missing_cols}", file=sys.stderr)
        # If critical columns are missing, stop refinement
        sys.exit(1)

def save_refined_data(df, output_path):
    """Saves the refined DataFrame to a new CSV file."""
    
if __name__ == "__main__":
    main()

