"""
sensitive data has been redacted/generalized. 
"""
#IBP COnsolidation Template
import os
from datetime import datetime
import pandas as pd
#for the binary files please use "pyxlsb"
from pyxlsb import open_workbook as open_xlsb
import sys


# Don't touch:
# -------------------------------------------------------------------------------------------------------------------------------------------------------
# Get user id for path
username = os.getlogin()

# Table of parameters for variables
""" 
'dataset' is a callable object when connected to Power BI. Python itself doesn't have anything for it, 
but in PBI it returns a table/object with the same defined name as in Python. 
"""
parameter_table = dataset

"""
Table is populated by paramteres in PBI, Python here takes the dataset object and 'checks' / uses iloc to get back values,
that the user stored as parameter in PBI.
The 'print' calls are only for error checks in VSCode, they shouldn't make a difference in PBI. 
"""
# Year to look at - '2023', '2024', '2025', ...
IBP_year = parameter_table.iloc[0, 0]
# Change file name, depending on month
IBP_file_name = parameter_table.iloc[0, 1]
# If looking for east data change zone to 'East', be carefull of capitalization
IBP_zone = parameter_table.iloc[0, 2]
# Location of where the end files will be saved
# If you want to save it 
IBP___folder_name__ = parameter_table.iloc[0, 3]
# The name of the sheet
IBP_sheet_name = "By Category"
# If working for east, change this to 'East' 
IBP_file_prefix = parameter_table.iloc[0, 4]
print("___ Check 1 - Global variables adjusted.")

# Can be changed:
# -------------------------------------------------------------------------------------------------------------------------------------------------------
# Define path and name of the end file
output_file = f"C:/Users/{username}/Desktop/{IBP___folder_name__}/Consolidated_data_{IBP_zone}_{IBP_year}_.xlsx"

# Path to the "Final templates" folder
templates_folder_path = os.path.join(f"C:/Users/{username}/company/Shared Documents/Planning/{IBP_year}/{IBP_file_name}/{IBP_zone}", "placeholder")

data_frames = []
# List of all .xlsb files in the "Final templates"
xlsb_files = [file for file in os.listdir(templates_folder_path) if file.endswith('.xlsb') and file.startswith(IBP_file_prefix)]

print("___ Check 2 - XLSB file check:")
if not xlsb_files:
    print("0 files collected, check IBP templates.")
else:
    print("Found the following files:")
    for file in xlsb_files:
        print(file)

print("___ Check 3 - Started retrieving data. ")
# Loop through each .xlsb file in the "Final templates" folder
for file in xlsb_files:
    print(f"___ Check 4 - Working on __{file}__.")
    file_path = os.path.join(templates_folder_path, file)

    try:
        print(f"___ Check 5 - Opening {file}.")
        with open_xlsb(file_path) as wb:
            with wb.get_sheet(IBP_sheet_name) as sheet:
                data = [[item.v for item in row] for row in sheet.rows()]

                if data:
                    df = pd.DataFrame(data[1:], columns=data[0])
                    data_frames.append(df)
                    print(f"___ Check 6 - Appended {file} data to data_frames.")
                else:
                    print(f"___ Warning: {file} contains no data!")
    except Exception as e:
        print(f"___ Error: Failed to process {file}. Reason: {e}")
    break # REMOVE BEFORE PROD ITS ONLY FOR TESTING

print("Start of consolidation.")
if data_frames:
    consolidated_data = pd.concat(data_frames, ignore_index=True)
    print("Consolidated. Formating it to Excel:")
    consolidated_data.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")

else:
    print("No data was processed.")
    df = pd.DataFrame()