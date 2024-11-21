import requests
import pandas as pd
import time

def clinical_scraper(condition, start_year, statuses, interventions, phases, sponsor_types):
    base_url = 'https://clinicaltrials.gov/api/v2/studies'
    
    # Convert parameters to proper query strings
    status_query = ','.join(statuses)
    intervention_query = ' OR '.join([f'AREA[InterventionType] {i}' for i in interventions])
    phase_query = ' OR '.join([f'AREA[Phase] {p}' for p in phases]) if phases else None
    sponsor_query = ' OR '.join(sponsor_types)

    # Construct advanced filter query
    advanced_filter = f'AREA[StartDate]RANGE[{start_year}-01-01,MAX]'
    if phase_query:
        advanced_filter += f' AND ({phase_query})'

    # Define API request parameters
    params = {
        'format': 'json',
        'query.cond': condition,
        'query.spons': sponsor_query,
        'filter.advanced': advanced_filter,
        'filter.overallStatus': status_query,
        'fields': 'NCTId,BriefTitle,Acronym,OverallStatus,StartDate,PrimaryCompletionDate,CompletionDate,StudyFirstPostDate,LastUpdatePostDate,StudyType,Phase,EnrollmentCount,LeadSponsorName,LeadSponsorClass,Condition,InterventionName,LocationFacility,LocationCity,LocationCountry',
        'pageSize': 100,
        'countTotal': 'true'
    }

    data_list = []
    total_count = None

    # Paginate through all results
    while True:
        print(f"Fetching data from: {base_url}")
        print(f"Parameters: {params}")
        
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            
            # Retrieve the total count of studies on the first request
            if total_count is None:
                total_count = data.get('totalCount', 0)
                print(f"Total studies matching criteria: {total_count}")

            studies = data.get('studies', [])
            print(f"Retrieved {len(studies)} studies in this batch")

            if not studies:
                print("No more studies found.")
                break

            for study in studies:
                protocol = study.get('protocolSection', {})
                identification = protocol.get('identificationModule', {})
                status = protocol.get('statusModule', {})
                design = protocol.get('designModule', {})
                sponsor = protocol.get('sponsorCollaboratorsModule', {}).get('leadSponsor', {})
                conditions = protocol.get('conditionsModule', {}).get('conditions', [])
                interventions = protocol.get('armsInterventionsModule', {}).get('interventions', [])
                locations = protocol.get('contactsLocationsModule', {}).get('locations', [])

                # Build row for DataFrame
                data_list.append({
                    "NCT ID": identification.get('nctId', 'Unknown'),
                    "Brief Title": identification.get('briefTitle', 'Unknown'),
                    "Overall Status": status.get('overallStatus', 'Unknown'),
                    "Start Date": status.get('startDateStruct', {}).get('date', 'Unknown'),
                    "Primary Completion Date": status.get('primaryCompletionDateStruct', {}).get('date', 'Unknown'),
                    "Completion Date": status.get('completionDateStruct', {}).get('date', 'Unknown'),
                    "Study First Post Date": status.get('studyFirstPostDateStruct', {}).get('date', 'Unknown'),
                    "Last Update Post Date": status.get('lastUpdatePostDateStruct', {}).get('date', 'Unknown'),
                    "Study Type": design.get('studyType', 'Unknown'),
                    "Phases": ', '.join(design.get('phases', [])),
                    "Enrollment": design.get('enrollmentInfo', {}).get('count', 'Unknown'),
                    "Lead Sponsor": sponsor.get('name', 'Unknown'),
                    "Lead Sponsor Type": sponsor.get('class', 'Unknown'),
                    "Sponsor Information": f"{sponsor.get('name', 'Unknown')} ({sponsor.get('class', 'Unknown')})",
                    "Conditions": ', '.join(conditions),
                    "Interventions": ', '.join([i.get('name', 'No intervention name listed') for i in interventions]),
                    "Locations": ', '.join([f"{loc.get('facility')} ({loc.get('city')}, {loc.get('country')})" for loc in locations])
                })

            # Check if there is a next page
            next_page_token = data.get('nextPageToken')
            if next_page_token:
                params['pageToken'] = next_page_token
                time.sleep(1)
            else:
                break
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Response content: {response.text}")
            break

    print(f"Total studies processed: {len(data_list)}")

    # Convert to DataFrame and sort
    df = pd.DataFrame(data_list)
    df.sort_values(by=["Start Date", "Overall Status", "Lead Sponsor"], inplace=True)
    return df