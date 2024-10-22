import requests
import pandas as pd
from google_patent_scraper import scraper_class
import json
from datetime import datetime, timedelta

# USPTO API endpoint and key
API_URL = "https://beta-api.uspto.gov/api/v1/patent/applications/search"
API_KEY = "rfbxhcdrspofadpnczkvodzctckduc"

# Headers for the API request
headers = {
    "X-API-Key": API_KEY,
    "accept": "application/json",
    "Content-Type": "application/json"
}

# Search query with specific date range
search_query = {
    "q": "applicationMetaData.firstApplicantName:\"Epizyme, Inc.\" AND applicationMetaData.patentNumber:*",
    "rangeFilters": [
        {
            "field": "applicationMetaData.grantDate",
            "valueFrom": "2021-10-21",
            "valueTo": "2024-10-20"
        }
    ],
    "fields": [
        "applicationMetaData.patentNumber",
        "applicationMetaData.inventionTitle",
        "applicationMetaData.firstApplicantName",
        "applicationMetaData.effectiveFilingDate",
        "applicationMetaData.applicationTypeLabelName",
        "applicationMetaData.applicationTypeCategory"
    ],
    "sort": [{"field": "applicationMetaData.grantDate", "order": "desc"}],
    "pagination": {"offset": 0, "limit": 100}
}

# Function to make API requests and handle pagination
def fetch_all_results(query):
    all_results = []
    offset = 0
    
    while True:
        query["pagination"]["offset"] = offset
        response = requests.post(API_URL, json=query, headers=headers)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            break
        
        data = response.json()
        results = data.get("patentFileWrapperDataBag", [])
        all_results.extend(results)
        
        if len(results) < query["pagination"]["limit"]:
            break
        
        offset += len(results)
    
    return all_results

# Fetch all results from USPTO
uspto_results = fetch_all_results(search_query)

# Initialize the Google Patent scraper with return_abstract=True
scraper = scraper_class(return_abstract=True)

# Process the scraped data
patent_data = []
for result in uspto_results:
    metadata = result.get("applicationMetaData", {})
    patent_number = metadata.get("patentNumber")
    
    if patent_number:
        print(f"Scraping data for patent {patent_number}")
        
        # Add patent to scraper
        scraper.add_patents(f"US{patent_number}")

# Scrape all patents
scraper.scrape_all_patents()

# Process the scraped data
for result in uspto_results:
    metadata = result.get("applicationMetaData", {})
    patent_number = metadata.get("patentNumber")
    
    if patent_number:
        full_patent_number = f"US{patent_number}"
        parsed_patent = scraper.parsed_patents.get(full_patent_number)
        
        if parsed_patent:
            patent_info = {
                "Patent ID": patent_number,
                "Title": metadata.get("inventionTitle", ""),
                "First Applicant Name": metadata.get("firstApplicantName", ""),
                "Effective Filing Date": metadata.get("effectiveFilingDate", ""),
                "Application Type": metadata.get("applicationTypeLabelName", ""),
                "Application Type Category": metadata.get("applicationTypeCategory", ""),
                "Publication Date": parsed_patent.get('pub_date', ''),
                "Grant Date": parsed_patent.get('grant_date', ''),
                "Abstract": parsed_patent.get('abstract_text', '')
            }
            patent_data.append(patent_info)
        else:
            print(f"No data found for patent {patent_number}")

# Create a DataFrame and save to Excel
if patent_data:
    df = pd.DataFrame(patent_data)
    excel_filename = "epizyme_patents_detailed_2021_2024.xlsx"
    df.to_excel(excel_filename, index=False)
    print(f"Results saved to {excel_filename}")
else:
    print("No patent data was scraped.")

# Print sample data for the first patent
if patent_data:
    print("\nSample data for the first patent:")
    print(json.dumps(patent_data[0], indent=2))
else:
    print("No patent data available to display.")