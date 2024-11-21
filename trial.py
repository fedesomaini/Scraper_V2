import pandas as pd
import tkinter as tk
import requests
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
        self.master.geometry("800x600")

        # Define conditions for dropdown
        self.conditions = [
            "All sites", "Acute Myeloid Leukemias", "Adnexa Other And Genital Female Other",
            "Adrenal Gland", "Ampulla Of Vater", "Anus, Anal Canal And Anorectum", "Appendix", "Biliary Other",
            "Bones And Joints", "Bones And Soft Tissue", "Brain (Malignant)", "Brain, CNS Other and Intracranial Gland (Benign and Borderline)",
            "Breast", "Buccal Mucosa", "Central Nervous System", "Cervix", "Chronic lymphocytic leukemia (CLL)/Small lymphocytic lymphoma",
            "CNS Other (Malignant)", "Colon And Rectum (Excluding Appendix)", "Corpus", "Digestive Other",
            "Digestive System", "Endocrine Other", "Endocrine System", "Esophagus", "Extrahepatic Bile Ducts",
            "Eye And Orbit", "Fallopian Tube", "Female Genital System", "Floor Of Mouth", "Gallbladder",
            "Genital Male Other", "Gum", "Head And Neck", "Heart, Mediastinum And Pleura", "Hematopoietic Neoplasms",
            "Hodgkin Lymphomas", "Hypopharynx", "Intracranial Gland (Malignant)", "Intrahepatic Bile Duct", "Kaposi Sarcoma",
            "Kidney Parenchyma", "Kidney Renal Pelvis", "Larynx", "Leukemias", "Lip", "Liver",
            "Lung And Bronchus", "Lymphoid Leukemias (excluding CLL/SLL)", "Lymphomas", "Major Salivary Glands",
            "Male Genital System", "Melanoma Of The Skin", "Meninges (Malignant)", "Mesothelioma",
            "Miscellaneous Hematopoietic Neoplasms", "Miscellaneous Neoplasms", "Mouth Other", "Myeloproliferative Neoplasms and Myelodysplastic Syndromes",
            "Nasal Cavity And Paranasal Sinuses", "Nasopharynx", "Non-Hodgkin Lymphomas", "Oropharynx", "Other Hematopoietic Neoplasms",
            "Other Leukemias", "Other Non-Epithelial Skin", "Ovary", "Palate Excluding Soft And Uvula", "Pancreas",
            "Parathyroid", "Penis", "Pharynx And Oral Cavity Other", "Placenta", "Plasma Cell Neoplasms and Immunoproliferative Diseases",
            "Precursor Lymphoid Neoplasms", "Prostate", "Respiratory Tract And Thorax", "Retroperitoneum And Peritoneum",
            "Sinus Other", "Skin", "Small Intestine", "Soft Tissue", "Stomach", "Testis", "Thymus", "Thyroid",
            "Tongue Anterior", "Trachea, And Respiratory Other", "Ureter", "Urethra", "Urinary Bladder",
            "Urinary Other", "Urinary System", "Vagina", "Vulva"
        ]

        # Sponsor types and their API mappings
        self.sponsor_vars = {
            "NIH": "NIH",
            "Other Government": ["FED", "OTHER_GOV"],
            "Individual": "IDIV",
            "Industry": "INDUSTRY",
            "Clinical Trial Network": "NETWORK",
            "Other": ["AMBIG", "OTHER", "UNKNOWN"]
        }

        self.create_widgets()

    def create_widgets(self):
        # Indication selection
        ttk.Label(self.master, text="Indication:*").grid(row=0, column=0, padx=15, pady=5, sticky="w")
        self.condition_var = tk.StringVar()
        self.condition_dropdown = ttk.Combobox(self.master, textvariable=self.condition_var, values=self.conditions, width=37)
        self.condition_dropdown.grid(row=0, column=1, padx=15, pady=5, sticky="w")
        self.condition_dropdown.set(self.conditions[0])  # Default value

        # Earliest start year for clinical trials
        ttk.Label(self.master, text="Earliest start year for clinical trials:*").grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.clinical_date_entry = ttk.Entry(self.master, width=40)
        self.clinical_date_entry.grid(row=1, column=1, padx=15, pady=5, sticky="w")

        # Clinical trial status checkboxes
        ttk.Label(self.master, text="Status of the clinical trial:*").grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.status_frame = ttk.Frame(self.master)
        self.status_frame.grid(row=2, column=1, padx=15, pady=5, sticky="w")

        self.status_vars = {}
        statuses = ["NOT_YET_RECRUITING", "RECRUITING", "ENROLLING_BY_INVITATION", "ACTIVE_NOT_RECRUITING",
                    "COMPLETED", "SUSPENDED", "TERMINATED", "WITHDRAWN"]
        for i, status in enumerate(statuses):
            var = tk.BooleanVar()
            ttk.Checkbutton(self.status_frame, text=status, variable=var).grid(row=i//2, column=i%2, sticky="w")
            self.status_vars[status] = var

        # Intervention Types
        ttk.Label(self.master, text="Intervention Types:*").grid(row=3, column=0, padx=15, pady=5, sticky="w")
        self.intervention_frame = ttk.Frame(self.master)
        self.intervention_frame.grid(row=3, column=1, padx=15, pady=5, sticky="w")

        self.intervention_vars = {}
        interventions = ["BEHAVIORAL", "BIOLOGICAL", "COMBINATION_PRODUCT", "DEVICE", "DIAGNOSTIC_TEST",
                         "DIETARY_SUPPLEMENT", "DRUG", "GENETIC", "PROCEDURE", "RADIATION", "OTHER"]
        for i, intervention in enumerate(interventions):
            var = tk.BooleanVar()
            ttk.Checkbutton(self.intervention_frame, text=intervention, variable=var).grid(row=i//3, column=i%3, sticky="w")
            self.intervention_vars[intervention] = var

        # Phase selection
        ttk.Label(self.master, text="Phase of clinical study:*").grid(row=4, column=0, padx=15, pady=5, sticky="w")
        self.phase_frame = ttk.Frame(self.master)
        self.phase_frame.grid(row=4, column=1, padx=15, pady=5, sticky="w")

        self.phase_vars = {}
        phases = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
        for i, phase in enumerate(phases):
            var = tk.BooleanVar()
            ttk.Checkbutton(self.phase_frame, text=phase, variable=var).grid(row=0, column=i, sticky="w")
            self.phase_vars[phase] = var

        # Sponsor Type Selection
        ttk.Label(self.master, text="Sponsor Type(s):*").grid(row=5, column=0, padx=15, pady=5, sticky="w")
        self.sponsor_frame = ttk.Frame(self.master)
        self.sponsor_frame.grid(row=5, column=1, padx=15, pady=5, sticky="w")

        # Create checkboxes for each sponsor type
        self.sponsor_check_vars = {}
        for i, (label, api_value) in enumerate(self.sponsor_vars.items()):
            var = tk.BooleanVar()
            ttk.Checkbutton(self.sponsor_frame, text=label, variable=var).grid(row=0, column=i, sticky="w")
            self.sponsor_check_vars[label] = var

        # Additional input fields for patent information
        ttk.Label(self.master, text="Name of company for patent search:").grid(row=6, column=0, padx=15, pady=5, sticky="w")
        self.company_name_entry = ttk.Entry(self.master, width=40)
        self.company_name_entry.grid(row=6, column=1, padx=15, pady=5, sticky="w")

        ttk.Label(self.master, text="Earliest year for patent application:").grid(row=7, column=0, padx=15, pady=5, sticky="w")
        self.patent_start_date_entry = ttk.Entry(self.master, width=40)
        self.patent_start_date_entry.grid(row=7, column=1, padx=15, pady=5, sticky="w")

        ttk.Label(self.master, text="Latest year for patent application:").grid(row=8, column=0, padx=15, pady=5, sticky="w")
        self.patent_end_date_entry = ttk.Entry(self.master, width=40)
        self.patent_end_date_entry.grid(row=8, column=1, padx=15, pady=5, sticky="w")

        # Run Button
        run_button = ttk.Button(self.master, text="Run Eurus", command=self.run_scraper)
        run_button.grid(row=9, columnspan=2, pady=20, sticky="ew")

    def run_scraper(self):
        # Gather all input values
        condition = '"' + self.condition_var.get().strip('"') + '"'
        start_year = self.clinical_date_entry.get()
        company_name = self.company_name_entry.get()
        patent_start_date = self.patent_start_date_entry.get()
        patent_end_date = self.patent_end_date_entry.get()

        # Validate start year
        try:
            start_year = int(start_year)
            if start_year < 1900 or start_year > 2100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid year (YYYY) for the clinical trial start year")
            return

        # Collect selected status, intervention types, phases, and sponsor types
        clinical_status = [status for status, var in self.status_vars.items() if var.get()]
        interventions = [intervention for intervention, var in self.intervention_vars.items() if var.get()]
        phases = [phase for phase, var in self.phase_vars.items() if var.get()]
        selected_sponsor_types = [val for label, var in self.sponsor_check_vars.items() if var.get() for val in self.sponsor_vars[label]]

        fda_date = self.patent_start_date_entry.get()  # Reused field for FDA date input

        # Run main scraper function with inputs
        run_main_scraper(condition, start_year, clinical_status, interventions, fda_date, phases, selected_sponsor_types, company_name, patent_start_date, patent_end_date)

def run_main_scraper(condition, start_year, clinical_status, interventions, fda_date, phases, sponsor_types, company_name, patent_start_date, patent_end_date):
    # Display inputs
    print(f"Running scraper with the following inputs:")
    print(f"Condition: {condition}")
    print(f"Start Year: {start_year}")
    print(f"Clinical Status: {clinical_status}")
    print(f"Interventions: {interventions}")
    print(f"FDA Approval Year: {fda_date}")
    print(f"Phases: {phases}")
    print(f"Sponsor Types: {sponsor_types}")
    print(f"Company Name: {company_name}")
    print(f"Patent Start Date: {patent_start_date}")
    print(f"Patent End Date: {patent_end_date}")

    # Call the clinical trials scraper
    try:
        clinical_df = clinical_scraper(condition, start_year, clinical_status, interventions, phases, sponsor_types)
        print(f"Clinical Trials Data Retrieved: {clinical_df.shape[0]} records")
    except Exception as e:
        print(f"Error during Clinical Trials Scraper: {e}")
        clinical_df = pd.DataFrame()

    # Call the FDA scraper
    try:
        fda_df = fda_scraper(condition.strip('"'), int(fda_date))
        print(f"FDA Data Retrieved: {fda_df.shape[0]} records")
    except Exception as e:
        print(f"Error during FDA Scraper: {e}")
        fda_df = pd.DataFrame()

    # Call the Epi scraper
    try:
        epi_df = run_epi_scraper(condition)
        print(f"Epi Data Retrieved: {epi_df.shape[0]} records")
    except Exception as e:
        print(f"Error during Epi-Scraper: {e}")
        epi_df = pd.DataFrame()

    # Call the USPTO scraper
    if company_name.strip():
        try:
            uspto_results = fetch_all_results(company_name, patent_start_date, patent_end_date)
            uspto_df = pd.DataFrame(process_patents(uspto_results))
            print(f"USPTO Data Retrieved: {uspto_df.shape[0]} records")
        except Exception as e:
            print(f"Error during USPTO Patent Scraper: {e}")
            uspto_df = pd.DataFrame()
    else:
        uspto_df = pd.DataFrame()

    # Process and combine company names for CIK matching
    clinical_companies = clinical_df['Lead Sponsor'] if 'Lead Sponsor' in clinical_df.columns else pd.Series()
    fda_companies = fda_df['Manufacturer Name'] if 'Manufacturer Name' in fda_df.columns else pd.Series()
    combined_companies = pd.concat([clinical_companies, fda_companies]).drop_duplicates().reset_index(drop=True)
    processed_companies_list = [company.replace(",", "").replace(" ", "").replace(".", "").lower() for company in combined_companies]

    # Obtain CIK Codes
    cik_companies_url = "https://raw.githubusercontent.com/fedesomaini/Scraper_V2/master/cik_companies.csv"
    response = requests.get(cik_companies_url)
    cik_df = pd.read_csv(StringIO(response.text))
    cik_df['processed_company_name'] = cik_df['Company Name'].str.replace(",", "").str.replace(" ", "").str.replace(".", "").str.lower()
    
    matched_companies = []
    for company in processed_companies_list:
        matches = process.extract(company, cik_df['processed_company_name'].tolist(), limit=1, scorer=fuzz.ratio)
        for match in matches:
            matched_index = cik_df[cik_df['processed_company_name'] == match[0]].index[0]
            matched_companies.append({
                'CIK Company Name': cik_df.loc[matched_index, 'Company Name'],
                'FDA+CT Company Name': combined_companies[processed_companies_list.index(company)],
                'CIK Code': cik_df.loc[matched_index, 'CIK Code'],
                'Match Score': match[1]
            })

    matched_df = pd.DataFrame(matched_companies)
    filtered_matched_df = matched_df[matched_df['Match Score'] >= 85]
    sorted_matched_df = filtered_matched_df.sort_values(by='Match Score', ascending=False)

    # Save all data to Excel
    output_path = r'C:\Webscraper\Scraper_V2\OutputSave\Save.xlsx'
    with pd.ExcelWriter(output_path) as writer:
        if not clinical_df.empty:
            clinical_df.to_excel(writer, sheet_name='Clinical Data', index=False)
        if not fda_df.empty:
            fda_df.to_excel(writer, sheet_name='FDA Data', index=False)
        if not epi_df.empty:
            epi_df.to_excel(writer, sheet_name='Epi Data', index=False)
        if not uspto_df.empty:
            uspto_df.to_excel(writer, sheet_name='USPTO Data', index=False)
        sorted_matched_df.to_excel(writer, sheet_name='Matches Comparison', index=False)
    
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()