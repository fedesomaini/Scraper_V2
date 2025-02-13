import requests
import pandas as pd
from google_patent_scraper import scraper_class
import json

# USPTO API endpoint and key
API_URL = "https://api.uspto.gov/api/v1/patent/applications/search"
API_KEY = "ehniyywcgsnyfkkgdtlinjimhpyuik"

# Old API Key for old USPTO portal: "rfbxhcdrspofadpnczkvodzctckduc". With this key, we have a 1,200,000 patent file wrapper, old API URL: "https://beta-api.uspto.gov/api/v1/patent/applications/search"

# Headers for the API request
headers = {
    "X-API-Key": API_KEY,
    "accept": "application/json",
    "Content-Type": "application/json"
}

def fetch_all_results(company_name, start_date, end_date):
    search_query = {
        "q": f'applicationMetaData.firstApplicantName:"{company_name}" AND applicationMetaData.patentNumber:*',
        "rangeFilters": [
            {
                "field": "applicationMetaData.grantDate",
                "valueFrom": start_date,
                "valueTo": end_date
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

    all_results = []
    offset = 0

    while True:
        search_query["pagination"]["offset"] = offset
        response = requests.post(API_URL, json=search_query, headers=headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            break

        data = response.json()
        results = data.get("patentFileWrapperDataBag", [])
        all_results.extend(results)

        if len(results) < search_query["pagination"]["limit"]:
            break

        offset += len(results)

    return all_results

# Initialize the Google Patent scraper with return_abstract=True
scraper = scraper_class(return_abstract=True)

def process_patents(uspto_results):
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

    return pd.DataFrame(patent_data)