#!/usr/bin/env python3

import pandas as pd
import json
import argparse
import sys
import logging

# ============ Logging Setup =============
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s",
    handlers=[
        logging.FileHandler("refine.log", mode="w"), # write all logs to refine.log
        logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

#============ Loading data and dictionary ======================
def load_data(csv_path):
    """Loads the CSV data into a pandas DataFrame.
    Args:
        csv_path (str): Path to the required data.

    Returns:
        df: data from the csv loaded into a dataframe.
    """
    try:
        df = pd.read_csv(csv_path)
        logger.info("Successfully loaded %d records.", len(df))
        print(df.info())                # can check for missing values and the types in each column
        return df
    # display errors on the console/terminal screen
    except FileNotFoundError:
        logger.error("Raw data file not found at %s", csv_path)
        raise
    except Exception as e:
        logger.error("Error loading data from %s: %s", csv_path, e)
        raise

def load_dictionary(dict_path):
    """Loads the data dictionary containing expected variable types and allowed values.
    Args:
        dict_path (dict): Path to the dictionary containing labels.
    """
    try:
        with open(dict_path, "r") as f:
            return json.load(f)
    # display errors on the console/terminal screen
    except FileNotFoundError:
        logger.error("Dictionary file not found at %s", dict_path)
        raise
    except Exception as e:
        logger.error("Error loading dictionary from %s: %s", dict_path, e)
        raise
    
#================= Refine function================================
def refine(df_raw, data_dict, id_col="SerialNum"):      
    # adding an ID argument instead of hard coding in SerialNum so the function can be reused with other data sets
    """ 
    Performs consistency checks and refines the raw census data:
    - validate types and admissible values using a data dictionary
    - removes duplicates and NaN values
    
    Args:
        df_raw: data frame containing the raw data in.
        data_dict (dict): data from the dictionary (codes and labels)
        id_col (str): name of the column containing identifiers

    Returns:
        df_refined: dataframe containing refined data 
        df_removed: dataframe containing removed/broken records
    """
    # catch errors without modifying the original
    df = df_raw.copy()

    # Ensure all required columns exist to start
    expected_cols = list(data_dict.keys())
    missing_cols = [col for col in expected_cols if col not in df.columns]

    if missing_cols:
        logger.error("Missing expected columns in raw data: %s", missing_cols)
        # If critical columns are missing, stop refinement
        sys.exit(1)

    # Remove duplicate serial numbers, keeping the first
    initial_count = len(df)
    df = df.drop_duplicates(subset=[id_col], keep='first')
    duplicates_removed = initial_count - len(df)

    if duplicates_removed > 0:
        logger.info("Removed %d duplicate records.", duplicates_removed)
    else:
        logger.info("No duplicate records found.")

    # Consistency Checks (Format and Admissible Values)
    # Track records that violate rules
    broken_records_indices = set() 
    
    # Iterate through variables defined in the dictionary
    for col_name, admissible_values_map in data_dict.items():

        # Check for Missing Values (NaN) first 
        # not necessary for this data set since there are no missing values but ensure reproducability for other data sets
        null_violations = df[df[col_name].isna()]
        if not null_violations.empty:
            logger.warning("Found %d records with MISSING (NaN) values in column '%s'.", len(null_violations), col_name)
            broken_records_indices.update(null_violations.index.tolist())

        # only validate non-null values against the dictionary
        df_non_null = df[df[col_name].notna()].copy()

        # The admissible keys are the codes in the dictionary (e.g, '1', '-8')
        admissible_keys = list(admissible_values_map.keys())

        # Column is treated as string for lookup against string dictionary keys
        df_non_null[col_name] = df_non_null[col_name].astype(str)
        
        # Find rows where the value is not in the admissible keys
        #'~' to select the rows that violate the condition
        violations = df_non_null[~df_non_null[col_name].isin(admissible_keys)]
        
        if not violations.empty:
            logger.warning("Found %d records with inadmissible values in '%s'.", len(violations), col_name)
            
            # Add indices of broken records to the set
            broken_records_indices.update(violations.index.tolist())
            
    # Remove all Broken Records
    if broken_records_indices:
        logger.info("Removing %d records due to inconsistencies.", len(broken_records_indices))
        
        # Create the refined DataFrame by dropping all broken indices
        df_refined = df.drop(index=broken_records_indices).reset_index(drop=True)
        # Create DataFrame of removed/broken records (empty if none)
        df_removed = df.loc[sorted(broken_records_indices)].copy().reset_index(drop=True)

    else:
        logger.info("No further inconsistencies found.")
        df_refined = df.copy()
        df_removed = pd.DataFrame(columns=df.columns)

    final_record_count = len(df_refined)
    logger.info("Refinement complete. Final record count: %d", final_record_count)
    return df_refined, df_removed

#================ saving functions ======================
def save_refined_data(df_refined, output_path):
    """Saves the refined DataFrame to a new CSV file.

    Args:
        df_refined: data frame with the refined data in.
        output_path (str): path to save refined data csv into.
    """
    df_refined.to_csv(output_path, index=False)
    logger.info("Refined data saved to: %s", output_path)

    # verification: Check if the file was written and has the expected number of records
    try:
        df_check = pd.read_csv(output_path)
        if len(df_check) == len(df_refined):
            logger.info("Verification successful: File count matches refined DataFrame count.")
        else: 
            logger.error("Verification failed: Saved file count (%d) does not match expected (%d).", len(df_check), len(df_refined))
            
    except Exception as e:
        logger.error("Failed to verify saved file %s: %s", output_path, e)

def save_removed_records(df_removed, removed_output_path):
    """Save the removed/broken records (if any) to a CSV for inspection.

    Args:
        df_removed: data frame with the removed/broken records in.
        removed_output_path (str): path to save removed/broken records csv into.
    """
    if df_removed.empty:
        logger.info("No removed/broken records to save.")
        return
    try:
        df_removed.to_csv(removed_output_path, index=False)
        logger.info("Removed/broken records saved to: %s", removed_output_path)
    except Exception as e:
        logger.error("Failed to save removed records to %s: %s", removed_output_path, e)

#========= for automating script from terminal =================   
def main():
    """Main function to execute the data refinement"""

    parser = argparse.ArgumentParser(
        description= "Automated script to upload the raw census dataset, refine the data and output a refined CSV file.")

    # Define arguments for input(raw data), output(refined data) and dictionary paths
    parser.add_argument('input_file', type=str, help='Path to the raw CSV data file')
    parser.add_argument('output_file', type=str, help='Path to save the refined CSV data file')
    parser.add_argument('dictionary_file', type=str, help='Path to the extended data dictionary JSON file')
    # Option to add path to save the removed records CSV
    parser.add_argument('--removed-output', type=str, default=None, help='Optional path to save removed/broken records CSV')

    args = parser.parse_args()

    try:
        # Load resources
        raw_df = load_data(args.input_file)
        data_dict = load_dictionary(args.dictionary_file)

        # Perform refinement
        refined_df, removed_df = refine(raw_df, data_dict)

        # Save the result
        save_refined_data(refined_df, args.output_file)

        # Save removed records if requested
        if args.removed_output:
            save_removed_records(removed_df, args.removed_output)
        
        # Verify script has ran
        logger.info("Script execution finished")
    
    except Exception as e:
        logger.exception("Script failed: %s", e)
        sys.exit(1)
    

if __name__ == "__main__":
    main()

