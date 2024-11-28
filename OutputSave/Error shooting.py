import requests

base_url = "https://clinicaltrials.gov/api/v2/studies"
params = {
    "format": "json",
    "filter.advanced": "AREA[LeadSponsorClass] FED",
    "fields": "NCTId,BriefTitle,OverallStatus,LeadSponsorName,LeadSponsorClass",
    "pageSize": 100,
}

response = requests.get(base_url, params=params)

if response.status_code == 200:
    print("Query successful. Response:")
    print(response.json())
else:
    print(f"Error: {response.status_code} - {response.text}")