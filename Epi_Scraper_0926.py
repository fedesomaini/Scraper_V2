import pandas as pd
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import openpyxl
import os
from datetime import datetime, timedelta
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

class CancerRateSelector:
    def __init__(self, master, condition):
        self.master = master
        self.master.title("Cancer Rate Selector")
        self.master.geometry("400x400")

        self.condition = condition
        self.selected_sites = []

        # Get the current year
        current_year = datetime.now().year
        # Calculate the start year (10 years ago)
        self.start_year = current_year - 10

        self.create_site_selection()

    def create_site_selection(self):
        self.site_frame = ttk.Frame(self.master)
        self.site_frame.pack(fill=tk.BOTH, expand=True)

        site_label = ttk.Label(self.site_frame, text="Select Site(s):")
        site_label.pack()

        self.site_listbox = tk.Listbox(self.site_frame, selectmode=tk.MULTIPLE)
        self.site_listbox.pack(fill=tk.BOTH, expand=True)

        sites = sorted(data['SITE'].unique())
        for site in sites:
            if self.condition.lower() in site.lower():
                self.site_listbox.insert(tk.END, site)

        save_button = ttk.Button(self.site_frame, text="Save Selection", command=self.save_selection)
        save_button.pack()

    def save_selection(self):
        self.selected_sites = [self.site_listbox.get(i) for i in self.site_listbox.curselection()]
        self.master.quit()

def run_epi_scraper(condition):
    root = tk.Tk()
    app = CancerRateSelector(root, condition)
    root.mainloop()

    # Get the current year
    current_year = datetime.now().year
    # Calculate the start year (10 years ago)
    start_year = current_year - 10

    # Filter the data based on selections
    filtered_data = data[
        (data['YEAR'] >= start_year) & 
        (data['YEAR'] <= current_year) & 
        (data['SITE'].isin(app.selected_sites))
    ]

    if filtered_data.empty:
        print("No data found for the selected combination of years and sites.")
        return pd.DataFrame()

    # Pivot the data to have SITE as rows and YEAR as columns
    pivoted_data = filtered_data.pivot(index='SITE', columns='YEAR', values='RATE')

    # Sort the columns (years) in ascending order
    pivoted_data = pivoted_data.sort_index(axis=1)

    # Add the indication as the first column
    pivoted_data.insert(0, 'Indication', condition)

    return pivoted_data

if __name__ == "__main__":
    # For testing purposes
    result = run_epi_scraper("Liver")
    print(result)