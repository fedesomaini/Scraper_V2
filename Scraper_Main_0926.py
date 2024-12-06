import pandas as pd
import tkinter as tk
import requests
import datetime
from io import StringIO
from rapidfuzz import process, fuzz
from tkinter import ttk, messagebox
from ClinicalTrials_Scraper_0926 import clinical_scraper
from FDA_Scraper_0926 import fda_scraper
from Epi_Scraper_0926 import run_epi_scraper
from USPTO_Patent import fetch_all_results, process_patents

class ScraperGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Eurus Input")
        self.master.geometry("800x700")  # Increased size to accommodate new checkboxes
        self.conditions = [
            "All sites", 
            "Acute Myeloid Leukemias", 
            "Adnexa Other And Genital Female Other",
            "Adrenal Gland", 
            "Ampulla Of Vater", 
            "Anus, Anal Canal And Anorectum",
            "Appendix",
            "Biliary Other",
            "Bones And Joints",
            "Bones And Soft Tissue",
            "Brain (Malignant)", 
            "Brain, CNS Other and Intracranial Gland (Benign and Borderline)",
            "Breast", 
            "Buccal Mucosa", 
            "Central Nervous System", 
            "Cervix",
            "Chronic lymphocytic leukemia (CLL)/Small lymphocytic lymphoma",
            "CNS Other (Malignant)", 
            "Colon And Rectum (Excluding Appendix)", 
            "Corpus",
            "Digestive Other", 
            "Digestive System", 
            "Endocrine Other", 
            "Endocrine System",
            "Esophagus", 
            "Extrahepatic Bile Ducts", 
            "Eye And Orbit", 
            "Fallopian Tube",
            "Female Genital System", 
            "Floor Of Mouth", 
            "Gallbladder", 
            "Genital Male Other",
            "Gum", 
            "Head And Neck", 
            "Heart, Mediastinum And Pleura", 
            "Hematopoietic Neoplasms",
            "Hodgkin Lymphomas", 
            "Hypopharynx", 
            "Intracranial Gland (Malignant)",
            "Intrahepatic Bile Duct", 
            "Kaposi Sarcoma", 
            "Kidney Parenchyma",
            "Kidney Renal Pelvis", 
            "Larynx", 
            "Leukemias", 
            "Lip", 
            "Liver",
            "Lung And Bronchus", 
            "Lymphoid Leukemias (excluding CLL/SLL)", 
            "Lymphomas",
            "Major Salivary Glands", 
            "Male Genital System", 
            "Melanoma Of The Skin",
            "Meninges (Malignant)", 
            "Mesothelioma", 
            "Miscellaneous Hematopoietic Neoplasms",
            "Miscellaneous Neoplasms", 
            "Mouth Other",
            "Myeloproliferative Neoplasms and Myelodysplastic Syndromes",
            "Nasal Cavity And Paranasal Sinuses", 
            "Nasopharynx", 
            "Non-Hodgkin Lymphomas",
            "Oropharynx", 
            "Other Hematopoietic Neoplasms", 
            "Other Leukemias",
            "Other Non-Epithelial Skin", 
            "Ovary", 
            "Palate Excluding Soft And Uvula",
            "Pancreas", 
            "Parathyroid", 
            "Penis", 
            "Pharynx And Oral Cavity Other", 
            "Placenta",
            "Plasma Cell Neoplasms and Immunoproliferative Diseases",
            "Precursor Lymphoid Neoplasms", 
            "Prostate", 
            "Respiratory Tract And Thorax",
            "Retroperitoneum And Peritoneum", 
            "Sinus Other", 
            "Skin", 
            "Small Intestine",
            "Soft Tissue", 
            "Stomach", 
            "Testis", 
            "Thymus", 
            "Thyroid", 
            "Tongue Anterior",
            "Trachea, And Respiratory Other", 
            "Ureter", 
            "Urethra", 
            "Urinary Bladder",
            "Urinary Other", 
            "Urinary System", 
            "Vagina", 
            "Vulva"
        ]

        self.create_widgets()

    def create_widgets(self):
        # Indication
        ttk.Label(self.master, text="Indication:*").grid(row=0, 
                                                        column=0, 
                                                        padx=15, 
                                                        pady=20, 
                                                        sticky="w")
        self.condition_var = tk.StringVar()
        self.condition_dropdown = ttk.Combobox(self.master, textvariable=self.condition_var, values=self.conditions, 
                                               width=37)
        self.condition_dropdown.grid(row=0, 
                                     column=1, 
                                     padx=15, 
                                     pady=20,
                                     sticky="w")
        self.condition_dropdown.set(self.conditions[0])  # Set default value

        # Clinical Trials Start Year
        ttk.Label(self.master, text="Earliest start year for clinical trials:*").grid(row=1, 
                                                                                     column=0, 
                                                                                     padx=15, 
                                                                                     pady=5, 
                                                                                     sticky="w")
        self.clinical_date_entry = ttk.Entry(self.master, 
                                             width=40)
        self.clinical_date_entry.grid(row=1, 
                                    column=1, 
                                    padx=15, 
                                    pady=5,
                                    sticky="w")

        # Clinical Trials Status
        ttk.Label(self.master, text="Status of the clinical trial:*").grid(row=2, 
                                                                          column=0, 
                                                                          padx=15, 
                                                                          pady=20, 
                                                                          sticky="w")
        self.status_frame = ttk.Frame(self.master)
        self.status_frame.grid(row=2, 
                               column=1, 
                               padx=15, 
                               pady=20, 
                               sticky="w")

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
            ttk.Checkbutton(self.status_frame, text=status, variable=var).grid(row=i//2,
                                                                               column=i%2, 
                                                                               sticky="w")
            self.status_vars[status] = var

        # Intervention Types
        ttk.Label(self.master, text="Intervention Types:*").grid(row=3, 
                                                                column=0, 
                                                                padx=15, 
                                                                pady=20, sticky="w")
        self.intervention_frame = ttk.Frame(self.master)
        self.intervention_frame.grid(row=3, 
                                     column=1, 
                                     padx=15, 
                                     pady=20, 
                                     sticky="w")

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
            ttk.Checkbutton(self.intervention_frame, 
                            text=intervention, 
                            variable=var).grid(row=i//3,
                                               column=i%3,
                                               sticky="w")
            self.intervention_vars[intervention] = var
        
        # Phase selection
        ttk.Label(self.master, 
            text="Phase of clinical study:*").grid(row=4,
                                                  column=0,
                                                  padx=15,
                                                  pady=20,
                                                  sticky="w")
        self.phase_frame = ttk.Frame(self.master)
        self.phase_frame.grid(row=4,
                              column=1,
                              padx=15,
                              pady=20,
                              sticky="w")

        self.phase_vars = {}
        phases = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
        for i, phase in enumerate(phases):
            var = tk.BooleanVar()
            ttk.Checkbutton(self.phase_frame,
                            text=phase,
                            variable=var).grid(row=0,
                                               column=i,
                                               sticky="w")  # All in row=0, but column=i
            self.phase_vars[phase] = var



        # FDA Approval Year
        ttk.Label(self.master, 
            text="Earliest approval year for labeled drug:*").grid(row=6,
                                                                  column=0,
                                                                  padx=15,
                                                                  pady=5,
                                                                  sticky="w")
        self.fda_date_entry = ttk.Entry(self.master,
                                        width=40)
        self.fda_date_entry.grid(row=6, 
                                 column=1, 
                                 padx=15, 
                                 pady=5,
                                 sticky="w")
        
        # Company Name Entry for USPTO Search
        ttk.Label(self.master, 
            text="Name of company for patent search:").grid(row=7,
                                                            column=0,
                                                            padx=15,
                                                            pady=5,
                                                            sticky="w")
        self.company_name_entry = ttk.Entry(self.master,
                                             width=40)
        self.company_name_entry.grid(row=7, 
                                      column=1, 
                                      padx=15, 
                                      pady=5,
                                      sticky="w")
        
        #Patent Date Range Start Entry
        ttk.Label(self.master, text="Earliest year for patent application:").grid(row=8,
                                                                                  column=0,
                                                                                  padx=15,
                                                                                  pady=5,
                                                                                  sticky="w")
        self.patent_start_date_entry = ttk.Entry(self.master, 
                                        width=40)
        self.patent_start_date_entry.grid(row=8,
                                 column=1,
                                 padx=15,
                                 pady=5,
                                 sticky="w")
        
        #Patent Date Range End Entry
        ttk.Label(self.master, text="Latest year for patent application:").grid(row=9, 
                                                                                column=0, 
                                                                                padx=15, 
                                                                                pady=5, 
                                                                                sticky="w")
        self.patent_end_date_entry = ttk.Entry(self.master, 
                                        width=40)
        self.patent_end_date_entry.grid(row=9, 
                                 column=1, 
                                 padx=15, 
                                 pady=5,
                                 sticky="w")

       # Sponsor Type
        ttk.Label(self.master, text="Sponsor Type(s):").grid(row=5, column=0, padx=15, pady=20, sticky="w")
        self.sponsor_frame = ttk.Frame(self.master)
        self.sponsor_frame.grid(row=5, column=1, padx=15, pady=20, sticky="w")

        # Updated Sponsor Types with mappings to API values
        self.sponsor_vars = {
        "Industry": ["INDUSTRY"],
        "Government": ["NIH", "FED", "OTHER_GOV"],  
        "Other": ["INDIV", "AMBIG", "NETWORK", "OTHER"]  
}

        self.sponsor_check_vars = {}
        for i, (label, api_value) in enumerate(self.sponsor_vars.items()):
            var = tk.BooleanVar()
            ttk.Checkbutton(self.sponsor_frame, text=label, variable=var).grid(row=0, column=i, sticky="w")
            self.sponsor_check_vars[label] = var

        # Run Button
        run_button=(ttk.Button)(self.master, 
                   text="Run Eurus", 
                   command=self.run_scraper)
        run_button.grid(row=10,
                        columnspan=2,
                        pady=20)

    def run_scraper(self):
        condition = '"' + self.condition_var.get().strip('"') + '"'
        start_year = self.clinical_date_entry.get()
        company_name = (self.company_name_entry.get)()
        patent_start_date = (self.patent_start_date_entry.get)()
        patent_end_date = (self.patent_end_date_entry.get)()
        fda_date = self.fda_date_entry.get() 

       # Retrieve and validate FDA Date
        fda_date = self.fda_date_entry.get()  # Retrieve the input

        try:
            fda_date = int(fda_date) if fda_date else None  # Make it optional
            if fda_date and (fda_date < 1900 or fda_date > 2100):  # Adjust range if needed
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid year (YYYY) for FDA approval year")
            return

       
        # Validate that start_year is a valid year
        try:
            start_year = int(start_year)
            if start_year < 1900 or start_year > 2100:  # Adjust range as needed
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid year (YYYY) for the clinical trial start year")
            return

        clinical_status =[status for status,(var) in (self.status_vars.items)() if var.get()]
        interventions =[intervention for intervention,(var) in (self.intervention_vars.items)() if var.get()]
        fda_date=self.fda_date_entry.get()

        # Collect selected phases
        phases = [phase for phase, var in self.phase_vars.items() if var.get()]


    def run_scraper(self):
        condition = '"' + self.condition_var.get().strip('"') + '"'
        start_year = self.clinical_date_entry.get()
        company_name = self.company_name_entry.get()

        # Get selected sponsor types 
        selected_sponsor_types = []
        for label, var in self.sponsor_check_vars.items():
            if var.get():
                api_value = self.sponsor_vars[label]
                if isinstance(api_value, list):
                    selected_sponsor_types.extend(api_value)
                else:
                    selected_sponsor_types.append(api_value)

        # Collect other parameters and run main scraper function
        clinical_status = [status for status, var in self.status_vars.items() if var.get()]
        interventions = [intervention for intervention, var in self.intervention_vars.items() if var.get()]
        phases = [phase for phase, var in self.phase_vars.items() if var.get()]
        patent_start_date = self.patent_start_date_entry.get()
        patent_end_date = self.patent_end_date_entry.get()
        fda_date = self.fda_date_entry.get()  # Retrieve the input

        if not all([condition, start_year, clinical_status, interventions, fda_date]):
            messagebox.showerror("Error", "Select fields must be filled")
            return

        # Destroy the GUI window before running the scraper
        self.master.quit()  # Stop the tkinter main loop
        self.master.destroy()  # Close the GUI window

        # Run the scraper with the collected inputs, including phases
        run_main_scraper(condition, start_year, clinical_status, interventions, fda_date, phases, selected_sponsor_types, company_name, patent_start_date, patent_end_date)

def run_main_scraper(condition, start_year, clinical_status, interventions, fda_date, phases, selected_sponsor_types, company_name, patent_start_date, patent_end_date):
    # Display inputs for debugging
    print(f"Running scraper with the following inputs:")
    print(f"Condition: {condition}")
    print(f"Start Year: {start_year}")
    print(f"Clinical Status: {clinical_status}")
    print(f"Interventions: {interventions}")
    print(f"FDA Approval Year: {fda_date}")
    print(f"Phases: {phases}")
    print(f"Sponsor Types: {selected_sponsor_types}")
    print(f"Company Name: {company_name}")
    print(f"Patent Start Date: {patent_start_date}")
    print(f"Patent End Date: {patent_end_date}")

    # Initialize empty DataFrames in case of exceptions
    clinical_df = pd.DataFrame()
    fda_df = pd.DataFrame()
    epi_df = pd.DataFrame()
    uspto_df = pd.DataFrame()

    # Call the clinical trials scraper and store the result in a DataFrame
    try:
        print("Starting Clinical Trials Scraper...")
        clinical_df = clinical_scraper(condition, start_year, clinical_status, interventions, phases, selected_sponsor_types)
        if not clinical_df.empty:
            print(f"Clinical Trials Data Retrieved: {clinical_df.shape[0]} records")
            clinical_df["Sponsor Information"] = clinical_df["Lead Sponsor"] + " (" + clinical_df["Lead Sponsor Type"] + ")"
            
            clinical_df.to_excel(writer, sheet_name='Clinical Data', index=False)
            print("Clinical Data saved with Sponsor Information.")

        else:
            print("No clinical trials data found.")
    except Exception as e:
        print(f"Error during Clinical Trials Scraper: {e}")

    # Call the FDA scraper and store the result in a DataFrame
    try:
        print("Starting FDA Scraper...")
        fda_condition = condition.strip('"')
        fda_df = fda_scraper(fda_condition, int(fda_date))
        if not fda_df.empty:
            print(f"FDA Data Retrieved: {fda_df.shape[0]} records")
        else:
            print("No FDA data found.")
    except Exception as e:
        print(f"Error during FDA Scraper: {e}")

    # Call the Epi scraper and store the result in a DataFrame
    try:
        print("Starting Epi-Scraper process...")
        epi_df = run_epi_scraper(condition)
        if not epi_df.empty:
            print(f"Epi Data Retrieved: {epi_df.shape[0]} records")
        else:
            print("No Epi data found.")
    except Exception as e:
        print(f"Error during Epi-Scraper: {e}")

    # Call the USPTO scraper and store the result in a DataFrame
    if company_name.strip():
        try:
            print("Starting USPTO Patent Scraper...")
            uspto_results = fetch_all_results(company_name, patent_start_date, patent_end_date)
            uspto_df = pd.DataFrame(process_patents(uspto_results))
            if not uspto_df.empty:
                print(f"USPTO Data Retrieved: {uspto_df.shape[0]} records")
            else:
                print("No USPTO data found.")
        except Exception as e:
            print(f"Error during USPTO Patent Scraper: {e}")
    else:
        print("Company Name is blank. Skipping USPTO Patent Scraper.")

    # Save all data to Excel
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = fr'C:\Webscraper\Scraper_V2\OutputSave\Save_{timestamp}.xlsx'

    try:
        with pd.ExcelWriter(output_path) as writer:
            if not clinical_df.empty:
                clinical_df.to_excel(writer, sheet_name='Clinical Data', index=False)
            if not fda_df.empty:
                fda_df.to_excel(writer, sheet_name='FDA Data', index=False)
            if not epi_df.empty:
                epi_df.to_excel(writer, sheet_name='Epi Data', index=False)
            if not uspto_df.empty:
                uspto_df.to_excel(writer, sheet_name='USPTO Data', index=False)
        print(f"Data saved to {output_path}")

    except Exception as e:
        print(f"Error saving data to Excel: {e}")
\

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