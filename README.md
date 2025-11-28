# CS5002-P3
This repository contains the refinement and analysis for the 2021 NISRA Census sample.
The project demonstrates reproducibility and reusability practices by separating the data processing logic into command-line executable scripts, focusing on loading and refinement, and Python modules containing functions, focusing on data mapping, complex plotting, and interactive visualisation.

It includes the following files:
-  `census-2021-public-microdata-teaching-sample.csv`: The raw data

-  `data_dictionary.json`: The extended dictionary,which provides the textual interpretations for values of the variables.

-  `refine_data.py`: The data loading and cleaning script. Can run from the terminal using the command python code/refine_data.py data/census-2021-public-microdata-teaching-sample.csv data/refined_data.csv data/data_dictionary.json. Can add an optional path e.g 'data/removed_records.csv' for saving broken/removed records. Depending on the environment in which it is ran, if 'python' doesn't work, locate the python path e.g '~\anaconda3\python.exe'. Can also import this module into the notebook to run and create the refined data CSV.

-  `data_analysis.py`: The reusable analysis and plotting functions.

-  `report_notebook.ipynb`: The primary analysis document. Open the notebook and run all cells sequentially to generate the analysis and static/interactive plots.


# Before running the notebook, ensure you have Python installed, and install the required Python libraries:
pip install pandas matplotlib numpy ipywidgets 