#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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

#================ Bar chart ==================================
def bar_chart(df, column_name, data_dict):
    """
    Generates a single bar chart for a categorical variable, handling data retrieval,
    labeling, rotation, and adding data labels for completeness.

    Args:
        df: The input dataframe.
        column_name (str): The column to analyse.
        data_dict (dict): The loaded JSON data dictionary.

    """
    
    # use the functions to retrieve the mapping and get the labelled data
    mapping = mapping_from_dict(column_name, data_dict)
    labels, counts = get_labels_and_counts(df, column_name, mapping)
    
    # Create a DataFrame for easy handling and sorting
    plot_data = pd.DataFrame({'Label': labels, 'Count': counts})
    
    # Set up the plot
    plt.figure(figsize=(12, 6))
    bars = plt.bar(
        plot_data['Label'], 
        plot_data['Count'], 
        color=plt.cm.plasma(np.linspace(0, 0.8, len(plot_data))) # Colour map for nicer visuals
    )

    # labels and title
    plt.title(f'Distribution of Records by {column_name}', fontsize=14)
    plt.xlabel(f'{column_name} Category', fontsize=12)
    plt.ylabel('Number of Records', fontsize=12)

    # For better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=30, ha='right') # Angled rotation for labels
    
    # Add data labels on top of the bars
    for bar in bars:
        yval = bar.get_height()
        # Position label slightly above the bar
        plt.text(bar.get_x() + bar.get_width()/2, yval + 20, yval, ha='center', va='bottom', fontsize=10)

    plt.tight_layout() # Ensures everything fits
    plt.show()

#================ Pie chart ==================================
def pie_chart(df, column_name, data_dict):
    """
    Generates a single pie chart for a categorical variable, including dynamic color mapping 
    and a legend placed outside the plot area.
    
    Args:
        df: The input DataFrame.
        column_name (str): The column to analyse.
        data_dict (dict): The loaded JSON data dictionary.
    """
    # use the functions to retrieve the mapping and get the labelled data
    mapping = mapping_from_dict(column_name, data_dict)
    labels, counts = get_labels_and_counts(df, column_name, mapping)
    total_count = sum(counts)

    # Set up plot
    plt.figure(figsize=(8, 8)) 

    wedges, texts, autotexts = plt.pie(
        counts,         
        autopct='%1.1f%%',    # Display percentage with 1dp
        startangle=90,
        textprops={'fontsize': 7, 'color': 'black'},
        colors=plt.cm.RdPu(np.linspace(0.1, 0.8, len(labels))) )

    plt.title(f'Percentage Distribution of {column_name} (Total: {total_count})', fontsize=14)

    plt.legend(
        wedges,             
        labels,      
        title=f"{column_name} Category",
        loc="center left",  
        bbox_to_anchor=(1, 0, 0.5, 1), # Anchor the legend outside the plot area
        fontsize=10,
        title_fontsize=12)

    plt.tight_layout() 
    plt.show()


#================= 2D tables =================================
def crosstab_groupby(df, col1, col2, data_dict):
    """
    Creates a cross-tabulation table with descriptive labels using pandas groupby().

    Args:
        df: The input dataframe.
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
#================ Pandas for cross tabulating =======================
def pandas_filtering(df, filter_col, filter_codes, groupby_col, data_dict, title):
    """
    Filters the DataFrame based on specific codes in one column and plots the distribution
    of a second column for the filtered subset.
    
    Args:
        df: The input dataframe.
        filter_col (str): The column used to filter records.
        filter_codes (list): The list of codes to keep in the filter_col.
        groupby_col (str): The column whose distribution is to be plotted.
        data_dict (dict): The loaded JSON data dictionary.
        title (str): The title for the resulting bar chart.
    """
    # Filter the DataFrame
    df_filtered = df[df[filter_col].astype(str).isin(filter_codes)].copy()

    # Get the label map for the column to be grouped by
    group_map = mapping_from_dict(groupby_col, data_dict)

    # Group by the target column and count the records
    distribution_counts = df_filtered[groupby_col].value_counts().sort_index()
    distribution_counts.index = distribution_counts.index.astype(str).map(group_map)

    # Prepare data for plotting
    plot_data = distribution_counts.reset_index()
    plot_data.columns = [groupby_col, 'Count']
    
    # set up the plot
    plt.figure(figsize=(10, 6))

    bars = plt.bar(
        plot_data[groupby_col], 
        plot_data['Count'], 
        color=plt.cm.viridis(np.linspace(0, 0.8, len(plot_data))) 
    )

    plt.title(title, fontsize=15)
    plt.xlabel(groupby_col, fontsize=12)
    plt.ylabel('Count of Individuals', fontsize=12)

    # Add data labels on top of the bars
    for bar in bars:
        yval = bar.get_height()
        # Position label slightly above the bar
        plt.text(bar.get_x() + bar.get_width()/2, yval + 20, yval, ha='center', va='bottom', fontsize=10)

    plt.xticks(rotation=15, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    # Also print the table for completeness
    print(distribution_counts.to_markdown())