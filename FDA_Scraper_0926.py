import requests
import pandas as pd
import os

def fda_scraper(indication_search_term, year):
    # Define the base URLs for the APIs
    base_url = 'https://api.fda.gov/drug/drugsfda.json'
    labels_base_url = 'https://api.fda.gov/drug/label.json'

    # Define negative phrases that indicate the drug is not approved for the indication
    negative_phrases = [
        "not approved for the prevention of",
        "not indicated for",
        "is not approved for",
        "not used for the treatment of",
        "should not be used for"
    ]

    # Define the minimum year for filtering
    min_year = year

    def contains_negative_phrase(text, negative_phrases, indication_search_term):
        for phrase in negative_phrases:
            if f"{phrase.lower()} {indication_search_term.lower()}" in text.lower():
                return True
        return False

    def filter_data_by_year(df, min_year):
        df['Submission Status Date'] = pd.to_datetime(df['Submission Status Date'], format='%Y%m%d', errors='coerce')
        filtered_df = df[df['Submission Status Date'].dt.year >= min_year]
        return filtered_df

    def fetch_data_from_api(url, limit=100):
        all_results = []
        skip = 0
        try:
            while True:
                paginated_url = f"{url}&limit={limit}&skip={skip}"
                print(f"Fetching: {paginated_url}")
                response = requests.get(paginated_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    if not results:
                        break
                    all_results.extend(results)
                    skip += limit
                else:
                    print(f"Failed to fetch data: {response.status_code}")
                    break
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        return all_results

    # Construct the search query for the labels API based on indication
    labels_query = f'indications_and_usage:"{indication_search_term}"'
    labels_url = f"{labels_base_url}?search={labels_query}"

    # Fetch all data from the labels API
    labels_results = fetch_data_from_api(labels_url)
    print(f"Number of records fetched from labels API: {len(labels_results)}")

    # Initialize an empty DataFrame
    fda_df = pd.DataFrame(columns=[
        "Application Number", "Brand Name", "Generic Name", "Manufacturer Name",
        "Dosage Form", "Marketing Status", "Submission Status Date", "Submission Type",
        "TE Code", "Substance Name", "RXCUI", "Route", "Pharm Class MOA",
        "Pharm Class PE", "Pharm Class EPC", "Package NDC", "Indication", "MOA"
    ])

    if labels_results:
        data_list = []
        processed_brands = set()

        for label in labels_results:
            indication = label.get('indications_and_usage', ['Not Provided'])[0]
            if contains_negative_phrase(indication, negative_phrases, indication_search_term):
                continue

            brand_names = label.get('openfda', {}).get('brand_name', ['Not Provided'])
            normalized_brand_names = set(name.lower() for name in brand_names if name != 'Not Provided')

            for brand_name in normalized_brand_names:
                if brand_name in processed_brands:
                    continue
                processed_brands.add(brand_name)

                query = f'openfda.brand_name:"{brand_name}"'
                url = f"{base_url}?search={query}&limit=1"
                print(url)

                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('results', [])
                        if results:
                            result = results[0]
                            data_list.append({
                                "Application Number": result.get('application_number', 'Not Provided'),
                                "Brand Name": brand_name,
                                "Generic Name": result.get('openfda', {}).get('generic_name', ['Not Provided'])[0],
                                "Manufacturer Name": result.get('openfda', {}).get('manufacturer_name', ['Not Provided'])[0],
                                "Dosage Form": result.get('products', [{}])[0].get('dosage_form', 'Not Provided'),
                                "Marketing Status": result.get('products', [{}])[0].get('marketing_status'),
                                "Submission Status Date": result.get('submissions', [{}])[0].get('submission_status_date', 'Not Provided'),
                                "Submission Type": result.get('submissions', [{}])[0].get('submission_type', 'Not Provided'),
                                "TE Code": result.get('products', [{}])[0].get('te_code', 'Not Provided'),
                                "Substance Name": result.get('openfda', {}).get('substance_name', ['Not Provided'])[0],
                                "RXCUI": result.get('openfda', {}).get('rxcui', ['Not Provided'])[0],
                                "Route": result.get('openfda', {}).get('route', ['Not Provided'])[0],
                                "Pharm Class MOA": result.get('openfda', {}).get('pharm_class_moa', ['Not Provided'])[0],
                                "Pharm Class PE": result.get('openfda', {}).get('pharm_class_pe', ['Not Provided'])[0],
                                "Pharm Class EPC": result.get('openfda', {}).get('pharm_class_epc', ['Not Provided'])[0],
                                "Package NDC": result.get('openfda', {}).get('package_ndc', ['Not Provided'])[0],
                                "Indication": indication,
                                "MOA": label.get('mechanism_of_action', ['Not Provided'])[0]
                            })
                    else:
                        print(f"Failed to fetch data for {brand_name}: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Request failed for {brand_name}: {e}")

        fda_df = pd.DataFrame(data_list)
        fda_df = filter_data_by_year(fda_df, min_year)
        print(fda_df)
    else:
        print("No results found in labels API.")

    return fda_df

if __name__ == "__main__":
    # Example usage
    indication = "liver cancer"
    year = 2000
    result = fda_scraper(indication, year)
    print(result)
    print(f"Shape of the DataFrame: {result.shape}")