import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import os
import sys
import subprocess
from rapidfuzz import fuzz, process
from ClinicalTrials_Scraper_0926 import clinical_scraper
from FDA_Scraper_0926 import fda_scraper
from Epi_Scraper_0926 import run_epi_scraper

#TESTING GIT UPLOAD


'''
This text is a test for github.
import os

# Use os.path to navigate directories and avoid hardcoding paths
current_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the current script
file_path = os.path.join(current_dir, "file.xlsx")  # File in the same directory as the script


'''

class ScraperGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Eurus Input")
        self.master.geometry("700x500")  # Increased size to accommodate new checkboxes

        self.create_widgets()

    def create_widgets(self):
        # Indication
        ttk.Label(self.master, text="Indication:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.condition_entry = ttk.Entry(self.master, width=30)
        self.condition_entry.grid(row=0, column=1, padx=5, pady=5)

        # Clinical Trials Start Year
        ttk.Label(self.master, text="Earliest start year for clinical trials:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.clinical_date_entry = ttk.Entry(self.master, width=30)
        self.clinical_date_entry.grid(row=1, column=1, padx=5, pady=5)

        # Clinical Trials Status
        ttk.Label(self.master, text="Status of the clinical trial:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.status_frame = ttk.Frame(self.master)
        self.status_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.status_vars = {}
        statuses = [
            "NOT_YET_RECRUITING",
            "RECRUITING",
            "ENROLLING_BY_INVITATION",
            "ACTIVE_NOT_RECRUITING",
            "COMPLETED",
            "SUSPENDED",
            "TERMINATED",
            "WITHDRAWN"
        ]
        for i, status in enumerate(statuses):
            var = tk.BooleanVar()
            ttk.Checkbutton(self.status_frame, text=status, variable=var).grid(row=i//2, column=i%2, sticky="w")
            self.status_vars[status] = var

        # Intervention Types
        ttk.Label(self.master, text="Intervention Types:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.intervention_frame = ttk.Frame(self.master)
        self.intervention_frame.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.intervention_vars = {}
        interventions = [
            "BEHAVIORAL",
            "BIOLOGICAL",
            "COMBINATION_PRODUCT",
            "DEVICE", 
            "DIAGNOSTIC_TEST",
            "DIETARY_SUPPLEMENT", 
            "DRUG", 
            "GENETIC",  
            "PROCEDURE", 
            "RADIATION", 
            "OTHER"
        ]
        for i, intervention in enumerate(interventions):
            var = tk.BooleanVar()
            ttk.Checkbutton(self.intervention_frame, text=intervention, variable=var).grid(row=i//3, column=i%3, sticky="w")
            self.intervention_vars[intervention] = var

        # FDA Approval Year
        ttk.Label(self.master, text="Earliest approval year for labeled drug:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.fda_date_entry = ttk.Entry(self.master, width=30)
        self.fda_date_entry.grid(row=4, column=1, padx=5, pady=5)

        # Run Button
        ttk.Button(self.master, text="Run Eurus", command=self.run_scraper).grid(row=5, column=0, columnspan=2, pady=20)

    def run_scraper(self):
        condition = self.condition_entry.get()
        start_year = self.clinical_date_entry.get()
        # Validate that start_year is a valid year
        try:
            start_year = int(start_year)
            if start_year < 1900 or start_year > 2100:  # Adjust range as needed
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid year (YYYY) for the clinical trial start year")
            return
        clinical_status = [status for status, var in self.status_vars.items() if var.get()]
        interventions = [intervention for intervention, var in self.intervention_vars.items() if var.get()]
        fda_date = self.fda_date_entry.get()

        if not all([condition, start_year, clinical_status, interventions, fda_date]):
            messagebox.showerror("Error", "All fields must be filled")
            return

        self.master.destroy()  # Close the GUI window

        # Run the scraper with the collected inputs
        run_main_scraper(condition, start_year, clinical_status, interventions, fda_date)

def run_main_scraper(condition, start_year, clinical_status, interventions, fda_date):
    print("Starting Clinical Trials Scraper...")
    clinical_df = clinical_scraper(condition, start_year, clinical_status, interventions)
    
    print("Starting FDA Scraper...")
    try:
        fda_df = fda_scraper(condition, int(fda_date))
        if fda_df is None or fda_df.empty:
            print("FDA scraper returned no results. Creating an empty DataFrame.")
            fda_df = pd.DataFrame()
    except Exception as e:
        print(f"Error in FDA scraper: {e}")
        fda_df = pd.DataFrame()  # Create an empty DataFrame if FDA scraper fails

    print("Starting Epi-Scraper process...")
    try:
        epi_df = run_epi_scraper(condition)  # Note: We're only passing the condition now
    except Exception as e:
        print(f"Error in Epi-Scraper: {e}")
        epi_df = pd.DataFrame()  # Create an empty DataFrame if Epi-Scraper fails

    # Save all data to Excel
    output_path = r'C:\Users\DaneCallow\Desktop\BSPROJ\Scraper\Newest\Scraper_Data.xlsx'
    with pd.ExcelWriter(output_path) as writer:
        clinical_df.to_excel(writer, sheet_name='Clinical Data', index=False)
        fda_df.to_excel(writer, sheet_name='FDA Data', index=False)
        epi_df.to_excel(writer, sheet_name='Epi Data', index=False)
    
    print(f"Data saved to {output_path}")

    # Extract company names
    clinical_companies = clinical_df['Lead Sponsor'] if 'Lead Sponsor' in clinical_df.columns else pd.Series()
    fda_companies = fda_df['Manufacturer Name'] if 'Manufacturer Name' in fda_df.columns else pd.Series()

    # Combine the contents and remove duplicates
    combined_companies = pd.concat([clinical_companies, fda_companies]).drop_duplicates().reset_index(drop=True)
    combined_companies_list = combined_companies.tolist()

    # Standardize the company names
    processed_companies_list = [company.replace(",", "").replace(" ", "").replace(".", "").lower() for company in combined_companies_list]

    print("The number of companies retrieved from FDA and CT scrapers is " + str(len(processed_companies_list)))

    # OBTAIN CIK CODES
    cik_companies_path = r'C:\Users\DaneCallow\Documents\GitHub\Scraper_V2\cik_companies.csv'
    cik_df = pd.read_csv(cik_companies_path)

    # Standardize company names in cik_df
    cik_df['processed_company_name'] = cik_df['Company Name'].str.replace(",", "").str.replace(" ", "").str.replace(".", "").str.lower()

    # Use approximate matching to find matches
    matched_companies = []
    for company in processed_companies_list:
        matches = process.extract(company, cik_df['processed_company_name'], limit=1, scorer=fuzz.ratio)
        for match in matches:
            matched_index = cik_df[cik_df['processed_company_name'] == match[0]].index[0]
            matched_companies.append({
                'CIK Company Name': cik_df.loc[matched_index, 'Company Name'],
                'FDA+CT Company Name': combined_companies_list[processed_companies_list.index(company)],
                'CIK Code': cik_df.loc[matched_index, 'CIK Code'],
                'Match Score': match[1]
            })
    # creating dataframe form matched companies
    matched_df = pd.DataFrame(matched_companies)

    # Filter out matches with low confidence score
    threshold = 90  # Adjust this threshold based on inspection
    filtered_matched_df = matched_df[matched_df['Match Score'] >= threshold]

    # Sort the filtered DataFrame by Match Score in descending order
    sorted_matched_df = filtered_matched_df.sort_values(by='Match Score', ascending=False)

    print(sorted_matched_df)
    print("Number of matches:", len(sorted_matched_df))

    # Append the sorted matches comparison data to the existing Excel file
    with pd.ExcelWriter(output_path, mode='a') as writer:
        sorted_matched_df.to_excel(writer, sheet_name='Matches Comparison', index=False)

    print(f"Sorted Matches Comparison data appended to {output_path}")

    # Extract CIK numbers for companies with match score above 95
    high_match_ciks = filtered_matched_df['CIK Code'].tolist()

    # Specify the path for the cikList.txt file
    cik_list_path = r'C:\Users\DaneCallow\Desktop\BSPROJ\Scraper\Newest\OneDrive_2024-09-26\EDGAR Scraper - Ashan\cikList.txt'

    # Write the CIK numbers to the text document, overwriting the file each time
    with open(cik_list_path, 'w') as file:
        for cik in high_match_ciks:
            file.write(str(cik) + '\n')

    print(f"CIK numbers for high-matching companies written to {cik_list_path}")
    
if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()

    # Path to the application
    app_path = r"C:\Users\DaneCallow\Desktop\BSPROJ\Scraper\Newest\OneDrive_2024-09-26\EDGAR Scraper - Ashan\ScraperTemplate.exe"

    # Run the application
    try:
        subprocess.run(app_path, check=True)
        print(f"Successfully ran application at {app_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error running application: {e}")
    except FileNotFoundError:
        print(f"Application not found at {app_path}")