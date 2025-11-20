#!/usr/bin/env python3

import pandas as pd
import json
import argparse
import sys

def load_data(csv_path):
    """Loads the CSV data into a pandas DataFrame."""
    print(f"Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Successfully loaded {len(df)} records.")
    print(df.info())                            # can check for missing values and the types in each column
    return df

def load_dictionary(dict_path):
    """Load the data dictionary containing expected variable types and allowed values."""
    print(f"Loading data dictionary: {dict_path}")
    with open(dict_path, "r") as f:
        return json.load(f)

def refine(df_raw, data_dict):
    """
    Performs consistency checks, removes duplicates and checks admissible values/formats to refine the data.
    """
    
if __name__ == "__main__":
    main()

