import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from ClinicalTrials_Scraper_0926 import clinical_scraper
from FDA_Scraper_0926 import fda_scraper
from Epi_Scraper_0926 import run_epi_scraper

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
        
        # Phase selection
        ttk.Label(self.master, text="Phase of clinical study:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.phase_frame = ttk.Frame(self.master)
        self.phase_frame.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        self.phase_vars = {}
        phases = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
        for i, phase in enumerate(phases):
            var = tk.BooleanVar()
            ttk.Checkbutton(self.phase_frame, text=phase, variable=var).grid(row=0, column=i, sticky="w")  # All in row=0, but column=i
            self.phase_vars[phase] = var

        # FDA Approval Year
        ttk.Label(self.master, text="Earliest approval year for labeled drug:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.fda_date_entry = ttk.Entry(self.master, width=30)
        self.fda_date_entry.grid(row=5, column=1, padx=5, pady=5)

        # Run Button
        ttk.Button(self.master, text="Run Eurus", command=self.run_scraper).grid(row=6, column=0, columnspan=2, pady=20)

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

        # Collect selected phases
        phases = [phase for phase, var in self.phase_vars.items() if var.get()]

        if not all([condition, start_year, clinical_status, interventions, fda_date]):
            messagebox.showerror("Error", "All fields must be filled")
            return

        # Destroy the GUI window before running the scraper
        self.master.quit()  # Stop the tkinter main loop
        self.master.destroy()  # Close the GUI window

        # Run the scraper with the collected inputs, including phases
        run_main_scraper(condition, start_year, clinical_status, interventions, fda_date, phases)

def run_main_scraper(condition, start_year, clinical_status, interventions, fda_date, phases):
    # Display inputs
    print(f"Running scraper with the following inputs:")
    print(f"Condition: {condition}")
    print(f"Start Year: {start_year}")
    print(f"Clinical Status: {clinical_status}")
    print(f"Interventions: {interventions}")
    print(f"FDA Approval Year: {fda_date}")
    print(f"Phases: {phases}")
    
    # Call the clinical trials scraper and store the result in a DataFrame
    try:
        print("Starting Clinical Trials Scraper...")
        clinical_df = clinical_scraper(condition, start_year, clinical_status, interventions, phases)
        print(f"Clinical Trials Data Retrieved: {clinical_df.shape[0]} records")
    except Exception as e:
        print(f"Error during Clinical Trials Scraper: {e}")
        clinical_df = pd.DataFrame()  # Create an empty DataFrame if something fails

    # Call the FDA scraper and store the result in a DataFrame
    try:
        print("Starting FDA Scraper...")
        fda_df = fda_scraper(condition, int(fda_date))
        if fda_df is None or fda_df.empty:
            print("FDA scraper returned no results. Creating an empty DataFrame.")
            fda_df = pd.DataFrame()
        print(f"FDA Data Retrieved: {fda_df.shape[0]} records")
    except Exception as e:
        print(f"Error during FDA Scraper: {e}")
        fda_df = pd.DataFrame()

    # Call the Epi scraper and store the result in a DataFrame
    try:
        print("Starting Epi-Scraper process...")
        epi_df = run_epi_scraper(condition)  # Assuming only condition is passed
        print(f"Epi Data Retrieved: {epi_df.shape[0]} records")
    except Exception as e:
        print(f"Error during Epi-Scraper: {e}")
        epi_df = pd.DataFrame()

    # Save all data to Excel
    output_path = r'C:\Webscraper\Scraper_V2\OutputSave.xlsx'
    with pd.ExcelWriter(output_path) as writer:
        if not clinical_df.empty:
            clinical_df.to_excel(writer, sheet_name='Clinical Data', index=False)
        if not fda_df.empty:
            fda_df.to_excel(writer, sheet_name='FDA Data', index=False)
        if not epi_df.empty:
            epi_df.to_excel(writer, sheet_name='Epi Data', index=False)
    
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()

    # Path to the application
    #app_path = r"C:\Users\DaneCallow\Desktop\BSPROJ\Scraper\Newest\OneDrive_2024-09-26\EDGAR Scraper - Ashan\ScraperTemplate.exe"

    # Run the application
   # try:
        #subprocess.run(app_path, check=True)
        #print(f"Successfully ran application at {app_path}")
   # except subprocess.CalledProcessError as e:
       # print(f"Error running application: {e}")
    #except FileNotFoundError:
       # print(f"Application not found at {app_path}")