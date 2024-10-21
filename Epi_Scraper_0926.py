import pandas as pd
import requests
from datetime import datetime
from io import BytesIO

# Replace this URL with the raw GitHub URL of your Excel file
github_excel_url = "https://raw.githubusercontent.com/fedesomaini/Scraper_V2/master/SEER_STAT_Epi.xlsx"

# Fetch the file from GitHub
response = requests.get(github_excel_url)
response.raise_for_status()  # This will raise an exception for HTTP errors

# Read the Excel file from the response content
data = pd.read_excel(BytesIO(response.content), engine='openpyxl')

print(f"Data loaded. Shape: {data.shape}")
print(f"Columns: {data.columns}")
print(f"First few rows:\n{data.head()}")
print(f"Unique YEAR values: {data['YEAR'].unique()}")
print(f"Unique SITE values: {data['SITE'].unique()}")

def run_epi_scraper(condition, selected_sites):
    """
    Function to run the epidemiological scraper with the given condition and selected sites.
    :param condition: The condition for which to filter the data.
    :param selected_sites: The list of selected sites from the main GUI.
    :return: A filtered and pivoted DataFrame with epidemiological data.
    """
    print(f"Running Epi Scraper for condition: {condition} and sites: {selected_sites}")

    # Get the current year
    current_year = datetime.now().year
    # Calculate the start year (10 years ago)
    start_year = current_year - 10

    # Filter the data based on the selected sites and year range
    filtered_data = data[
        (data['YEAR'] >= start_year) & 
        (data['YEAR'] <= current_year) & 
        (data['SITE'].isin(selected_sites))
    ]

    if filtered_data.empty:
        print("No data found for the selected combination of years and sites.")
        return pd.DataFrame()

    # Pivot the data to have SITE as rows and YEAR as columns
    pivoted_data = filtered_data.pivot(index='SITE', columns='YEAR', values='RATE')

    # Sort the columns (years) in ascending order
    pivoted_data = pivoted_data.sort_index(axis=1)

    # Add the condition as the first column
    pivoted_data.insert(0, 'Indication', condition)

    return pivoted_data

if __name__ == "__main__":
    # For testing purposes
    selected_sites = ["Liver", "Lung"]  # Example site selections passed from the main GUI
    result = run_epi_scraper("Liver", selected_sites)
    print(result)