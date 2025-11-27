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
    """Loads the data dictionary containing expected variable types and allowed values.
    Args:
        dict_path (dict): Path to the dictionary containing labels.
    """
    print(f"Loading data dictionary: {dict_path}")
    with open(dict_path, "r") as f:
        return json.load(f)
    
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
    # Track records that violate rules
    broken_records_indices = set() 
    
    # Iterate through variables defined in the dictionary
    for col_name, admissible_values_map in data_dict.items():
        print(f"Checking column: {col_name}")

        # The admissible keys are the codes in the dictionary (e.g, '1', '-8')
        admissible_keys = list(admissible_values_map.keys())

        # Column is treated as string for lookup against string dictionary keys
        df[col_name] = df[col_name].astype(str)
        
        # Find rows where the value is not in the admissible keys
        #'~' to select the rows that violate the condition
        violations = df[~df[col_name].isin(admissible_keys)]
        
        if not violations.empty:
            print(f"Found {len(violations)} records with inadmissible values in '{col_name}'.")
            
            # Print information about broken records
            print("Example broken records:")
            print(violations[['SerialNum', col_name]].head())
            
            # Add indices of broken records to the set
            broken_records_indices.update(violations.index.tolist())
            
    # Remove all Broken Records
    if broken_records_indices:
        print(f"Removing {len(broken_records_indices)} records due to inconsistencies.")
        
        # Create the refined DataFrame by dropping all broken indices
        df_refined = df.drop(index=broken_records_indices).reset_index(drop=True)
    else:
        print("No further inconsistencies found.")
        df_refined = df.copy()

    final_record_count = len(df_refined)
    print(f"Refinement complete. Final record count: {final_record_count}")
    return df_refined

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

