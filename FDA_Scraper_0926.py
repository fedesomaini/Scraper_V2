import requests
import pandas as pd
from urllib.parse import quote_plus

def fda_scraper(indication_search_term, year):
    base_url = 'https://api.fda.gov/drug/drugsfda.json'
    labels_base_url = 'https://api.fda.gov/drug/label.json'

    negative_phrases = [
        "not approved for the prevention of",
        "not indicated for",
        "is not approved for",
        "not used for the treatment of",
        "should not be used for"
    ]

    def fetch_data_from_api(url, limit=100):
        all_results = []
        skip = 0
        while True:
            paginated_url = f"{url}&limit={limit}&skip={skip}"
            print(f"Fetching: {paginated_url}")
            try:
                response = requests.get(paginated_url, timeout=10)
                response.raise_for_status()
                data = response.json()
                results = data.get('results', [])
                if not results:
                    break
                all_results.extend(results)
                skip += limit
                if skip >= 1000:  # Limit to 1000 results for efficiency
                    break
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                break
        return all_results

    # Construct the search query for the labels API
    encoded_indication = quote_plus(f'"{indication_search_term}"')
    labels_query = f'indications_and_usage:{encoded_indication}+AND+openfda.product_type:"PRESCRIPTION"'
    labels_url = f"{labels_base_url}?search={labels_query}"

    # Fetch data from the labels API
    labels_results = fetch_data_from_api(labels_url)
    print(f"Number of records fetched from labels API: {len(labels_results)}")

    data_list = []
    processed_brands = set()

    for label in labels_results:
        indication = label.get('indications_and_usage', ['Not Provided'])[0]
        if any(phrase in indication.lower() for phrase in negative_phrases):
            continue

        brand_names = label.get('openfda', {}).get('brand_name', ['Not Provided'])
        for brand_name in set(name.lower() for name in brand_names if name != 'Not Provided'):
            if brand_name in processed_brands:
                continue
            processed_brands.add(brand_name)

            query = f'openfda.brand_name:"{brand_name}" AND submissions.submission_status_date:[{year}0101 TO 99991231]'
            url = f"{base_url}?search={quote_plus(query)}&limit=1"

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
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
            except requests.exceptions.RequestException as e:
                print(f"Request failed for {brand_name}: {e}")

    fda_df = pd.DataFrame(data_list)
    return fda_df

if __name__ == "__main__":
    indication = "head and neck cancer"
    year = 2000
    result = fda_scraper(indication, year)
    print(result)
    print(f"Shape of the DataFrame: {result.shape}")