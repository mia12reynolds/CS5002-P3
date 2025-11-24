#!/usr/bin/env python3

import pandas as pd
import json
import argparse
import sys

#============ Loading data and dictionary ======================
def load_data(csv_path):
    """Loads the CSV data into a pandas DataFrame.
    Args:
        csv_path (str): Path to the required data.

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
        dict_path (dict): Path to the dictionary containing labels.
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
        data_dict (dict): data from the dictionary (codes and labels)

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

    # Remove duplicate serial numbers, keeping the first
    initial_count = len(df)
    df = df.drop_duplicates(subset=["SerialNum"], keep='first')
    duplicates_removed = initial_count - len(df)
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} duplicate records.")
    else:
        print("No duplicate records found.")

    # Consistency Checks (Format and Admissible Values)

#================ saving function ======================
def save_refined_data(df_refined, output_path):
    """Saves the refined DataFrame to a new CSV file.

    Args:
        df_refined: data frame with the refined data in.
        output_path (str): path to save refined data csv into.
    """
    df_refined.to_csv(output_path, index=False)
    print(f"refined data saved to: {output_path}")

    # verification: Check if the file was written and has the expected number of records
    df_check = pd.read_csv(output_path)
    if len(df_check) == len(df_refined):
        print("Verification successful: File count matches refined DataFrame count.")
    else:
        print("Verification failed: Saved file count mismatch.", file=sys.stderr)

#========= for automating script from terminal =================   
def main():
    """Main function to execute the data refinement"""

    parser = argparse.ArgumentParser(
        description= "Automated script to upload the raw census dataset, refine the data and output a refined CSV file.")

    # Define arguments for input(raw data), output(refined data) and dictionary paths
    parser.add_argument('input_file', type=str, help='Path to the raw CSV data file')
    parser.add_argument('output_file', type=str, help='Path to save the refined CSV data file')
    parser.add_argument('dictionary_file', type=str, help='Path to the extended data dictionary JSON file')

    args = parser.parse_args()

    # Load resources
    raw_df = load_data(args.input_file)
    data_dict = load_dictionary(args.dictionary_file)
    
    # Perform refinement
    refined_df = refine(raw_df, data_dict)
    
    # Save the result
    save_refined_data(refined_df, args.output_file)

    # Verify script has ran
    print("Script execution finished")

if __name__ == "__main__":
    main()

