import requests
import pandas as pd
from datetime import datetime, date
import time

def clinical_scraper(condition, start_year, statuses, interventions, phases):
    base_url = 'https://clinicaltrials.gov/api/v2/studies'
    
    # Convert statuses to the format expected by the API
    status_query = ','.join(statuses)
    
    # Convert interventions to the format expected by the API
    intervention_query = ' OR '.join([f'AREA[InterventionType] {i}' for i in interventions])

    # Convert phases to the format expected by the API
    if phases:
        phase_query = ' OR '.join([f'AREA[Phase] {p}' for p in phases])
    else:
        phase_query = None

    # Create the advanced filter query
    advanced_filter = f'AREA[StartDate]RANGE[{start_year}-01-01,MAX]'
    if phase_query:
        advanced_filter += f' AND ({phase_query})'

    params = {
        'format': 'json',
        'query.cond': condition,
        'query.intr': intervention_query,
        'query.spons': 'AREA[LeadSponsorClass] INDUSTRY',
        'filter.advanced': advanced_filter,
        'filter.overallStatus': status_query,
        'fields': 'NCTId,BriefTitle,Acronym,OverallStatus,StartDate,PrimaryCompletionDate,CompletionDate,StudyFirstPostDate,LastUpdatePostDate,StudyType,Phase,EnrollmentCount,LeadSponsorName,LeadSponsorClass,Condition,InterventionName,LocationFacility,LocationCity,LocationCountry',
        'pageSize': 100,
        'countTotal': 'true'
    }

    data_list = []
    total_count = None

    while True:
        print(f"Fetching data from: {base_url}")
        print(f"Parameters: {params}")
        
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            
            if total_count is None:
                total_count = data.get('totalCount', 0)
                print(f"Total studies matching criteria: {total_count}")

            studies = data.get('studies', [])
            print(f"Retrieved {len(studies)} studies in this batch")

            if not studies:
                print("No more studies found")
                break

            for study in studies:
                nct_id = study.get('protocolSection', {}).get('identificationModule', {}).get('nctId')
                overall_status = study.get('protocolSection', {}).get('statusModule', {}).get('overallStatus')
                sponsor_type = study.get('protocolSection', {}).get('sponsorCollaboratorsModule', {}).get('leadSponsor', {}).get('class')
                start_date = study.get('protocolSection', {}).get('statusModule', {}).get('startDateStruct', {}).get('date')

                print(f"Processing study {nct_id} - Status: {overall_status}, Sponsor Type: {sponsor_type}")

                data_list.append({
                    "NCT ID": nct_id,
                    "Brief Title": study.get('protocolSection', {}).get('identificationModule', {}).get('briefTitle'),
                    "Acronym": study.get('protocolSection', {}).get('identificationModule', {}).get('acronym'),
                    "Overall Status": overall_status,
                    "Start Date": start_date,
                    "Primary Completion Date": study.get('protocolSection', {}).get('statusModule', {}).get('primaryCompletionDateStruct', {}).get('date'),
                    "Completion Date": study.get('protocolSection', {}).get('statusModule', {}).get('completionDateStruct', {}).get('date'),
                    "Study First Post Date": study.get('protocolSection', {}).get('statusModule', {}).get('studyFirstPostDateStruct', {}).get('date'),
                    "Last Update Post Date": study.get('protocolSection', {}).get('statusModule', {}).get('lastUpdatePostDateStruct', {}).get('date'),
                    "Study Type": study.get('protocolSection', {}).get('designModule', {}).get('studyType'),
                    "Phases": ', '.join(study.get('protocolSection', {}).get('designModule', {}).get('phases', [])),
                    "Enrollment": study.get('protocolSection', {}).get('designModule', {}).get('enrollmentInfo', {}).get('count'),
                    "Lead Sponsor": study.get('protocolSection', {}).get('sponsorCollaboratorsModule', {}).get('leadSponsor', {}).get('name'),
                    "Lead Sponsor Type": sponsor_type,
                    "Conditions": ', '.join(study.get('protocolSection', {}).get('conditionsModule', {}).get('conditions', [])),
                    "Interventions": ', '.join([intervention.get('name', 'No intervention name listed') for intervention in study.get('protocolSection', {}).get('armsInterventionsModule', {}).get('interventions', [])]),
                    "Locations": ', '.join([f"{location.get('facility')} ({location.get('city')}, {location.get('country')})" for location in study.get('protocolSection', {}).get('contactsLocationsModule', {}).get('locations', [])])
                })

            next_page_token = data.get('nextPageToken')
            if next_page_token:
                params['pageToken'] = next_page_token
                time.sleep(1)  # Add a 1-second delay between requests
            else:
                break
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Response content: {response.text}")
            break

    print(f"\nSummary:")
    print(f"Total studies matching criteria: {total_count}")
    print(f"Studies retrieved and processed: {len(data_list)}")

    # Sort the data_list
    sorted_data = sorted(data_list, 
                         key=lambda x: (x['Start Date'] or '', x['Overall Status'] or '', x['Lead Sponsor'] or ''))

    df = pd.DataFrame(sorted_data)
    
    # Create a file name based on the indication and current date
    #today = date.today().strftime("%Y%m%d")
    #file_name = f"{condition.replace(' ', '_')}_{today}.csv"
    
    # Save the DataFrame to a specific folder with the dynamic file name
    #output_path = r'C:\Webscraper\Scraper_V2\OutputSave' + '\\' + file_name
    #df.to_csv(output_path, index=False)
    #print(f"Data saved to {output_path}")

    return df


# Example usage
# if __name__ == "__main__":
#     indication = "Melanoma"
#     start_year = 2020
#     statuses = ["RECRUITING", "ACTIVE_NOT_RECRUITING"]
#     interventions = ["DRUG", "BIOLOGICAL"]
#     df = clinical_scraper(indication, start_year, statuses, interventions)