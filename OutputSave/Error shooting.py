import requests
import pandas as pd
import time

def clinical_scraper(condition, start_year, statuses, interventions, phases, sponsor_types):
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

    # Add sponsor_types to the advanced filter query
    if sponsor_types:
        sponsor_query = ' OR '.join([f'AREA[LeadSponsorClass] {s}' for s in sponsor_types])
        advanced_filter += f' AND ({sponsor_query})'

    # Create the parameters for the API request
    params = {
        'format': 'json',
        'query.cond': condition,
        'query.intr': intervention_query,
        'filter.advanced': advanced_filter,
        'filter.overallStatus': status_query,
        'fields': (
            'NCTId,BriefTitle,Acronym,OverallStatus,StartDate,PrimaryCompletionDate,CompletionDate,'
            'StudyFirstPostDate,LastUpdatePostDate,StudyType,Phase,EnrollmentCount,LeadSponsorName,'
            'LeadSponsorClass,Condition,InterventionName,LocationFacility,LocationCity,LocationCountry'
        ),
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
                    "Overall Status": overall_status,
                    "Start Date": start_date,
                    "Sponsor Type": sponsor_type
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

    df = pd.DataFrame(data_list)
    return df

