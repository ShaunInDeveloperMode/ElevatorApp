# Google Search API Data Fetcher Script
#
# This script fetches data from the Google Search API for a list of keywords,
# saves the responses as JSON files, and updates the keywords CSV file with
# the last fetched date.
#
# Script Flow:
# 1. Reads API credentials from 'APIFetchData.csv'.
# 2. Reads keywords from 'unioned_keywords.csv'.
# 3. Filters keywords that haven't been fetched yet.
# 4. Fetches data from Google Search API for each keyword.
# 5. Saves API responses as JSON files in 'GSAPI_Transaction_Log'.
# 6. Updates 'unioned_keywords.csv' with last fetched date.
# 7. Logs errors to 'GSAPI_Transaction_Log/error_report.csv'.
#
# Configuration:
#   - 'APIFetchData.csv': API credentials file.
#   - 'unioned_keywords.csv': keywords file.
#   - 'GSAPI_Transaction_Log': API response log folder.
#   - MAX_ATTEMPTS: Maximum attempts for API fetch.
#   - DAILY_LIMIT: Daily limit for API calls.
#
# Requirements:
#   - Google Search API credentials.
#   - pandas, requests, and json libraries.
#
# Usage:
#   1. Replace 'APIFetchData.csv' and 'unioned_keywords.csv' with your data.
#   2. Update 'GSAPI_Transaction_Log' folder path if necessary.
#   3. Run the script.

import pandas as pd
import requests
import json
from datetime import datetime
import os

# Base directory constant (root folder)
BASE_DIR = r'C:\Users\himpr\Desktop\Python Training'

# Subfolder for non-log files (you can modify this as needed)
NON_LOG_SUBFOLDER = 'Elevator App'

# Constants
CSV_PATH = os.path.join(BASE_DIR, NON_LOG_SUBFOLDER, 'APIFetchData.csv')
KEYWORDS_PATH = os.path.join(
    BASE_DIR, NON_LOG_SUBFOLDER, 'unioned_keywords.csv')

# Path for API logs
API_LOG_PATH = os.path.join(BASE_DIR, 'GSAPI_Transaction_Log')
ERROR_REPORT_PATH = os.path.join(API_LOG_PATH, 'error_report.csv')

MAX_ATTEMPTS = 5  # Max attempts for API fetch

# Function to log errors


def log_error(api_name, error_type, error_desc):
    error_data = {
        'API_Name': api_name,
        'Date_Added': datetime.now().strftime('%Y-%m-%d'),
        'Error Type': error_type,
        'Error Description': error_desc
    }
    # Append error to CSV
    if not os.path.exists(ERROR_REPORT_PATH):
        pd.DataFrame([error_data]).to_csv(ERROR_REPORT_PATH, index=False)
    else:
        pd.DataFrame([error_data]).to_csv(ERROR_REPORT_PATH,
                                          mode='a', header=False, index=False)


# Read the CSV file for credentials
try:
    df_creds = pd.read_csv(CSV_PATH, delimiter=',', encoding='cp1252')
    api_info = df_creds[df_creds['API_Name'] ==
                        'Google_Search_API_Google_Search_Text'].iloc[0]
    google_api_url = api_info['AddAPI_URL']
    google_api_key = api_info['AddAPI_API_Key']
    custom_search_engine_id = api_info['AddAPI_Password']
    ORIGINAL_API_NAME = api_info['API_Name']
    API_DESCRIPTION = api_info['AddAPI_Description']
except Exception as e:
    log_error("Google_Search_API_Google_Search_Text", "CSV Read Error", str(e))
    raise e

# Read the CSV file with keywords
df_keywords = pd.read_csv(KEYWORDS_PATH, delimiter=',', encoding='cp1252')
df_keywords = df_keywords.astype(
    {'Keyword': 'object', 'LastDateFetched': 'object'})

# Preserve the original df_keywords and create a filtered version to work with
df_unfetched_keywords = df_keywords[df_keywords['LastDateFetched'].isna() | (
    df_keywords['LastDateFetched'] == '')].copy()

# Manually add the 'API_Name' and 'API_Description' columns
df_unfetched_keywords['API_Name'] = ORIGINAL_API_NAME
df_unfetched_keywords['API_Description'] = API_DESCRIPTION

# Function to fetch data from Google Search API


def fetch_google_search(api_url, api_key, search_engine_id, query):
    try:
        full_url = f"{api_url}?key={api_key}&cx={search_engine_id}&q={query}"
        response = requests.get(full_url)
        if response.status_code == 200:
            json_data = response.json()
            json_data['Original_API_Name'] = ORIGINAL_API_NAME
            json_data['API_Description'] = API_DESCRIPTION
            json_data['AddAPI_URL'] = api_url  # To track the API URL used
            return json_data
        else:
            raise Exception(
                f"API Error: {response.status_code} - {response.text}")
    except Exception as e:
        log_error(ORIGINAL_API_NAME, "API Request Error", str(e))
        return None


# I changed Max Attempts to be the Daily Limit so that I only have to make 1 update when adjusting max attempts for testing purposes.
DAILY_LIMIT = MAX_ATTEMPTS
successful_calls = 0

for idx, row in df_unfetched_keywords.iterrows():
    if successful_calls >= DAILY_LIMIT:
        print(f"Reached testing limit of {DAILY_LIMIT}, stopping for now.")
        break

    query = row['Keyword']
    attempts = 0
    success = False

    while attempts < MAX_ATTEMPTS and not success:
        result = fetch_google_search(
            google_api_url, google_api_key, custom_search_engine_id, query)
        if result:
            current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"{row['API_Name']}_{current_datetime}.json"
            with open(os.path.join(API_LOG_PATH, filename), 'w') as json_file:
                json.dump(result, json_file)
            print(f"Saved API response for {query} as {filename}")

            # Update the original df_keywords for the current query
            df_keywords.loc[df_keywords['Keyword'] ==
                            query, 'LastDateFetched'] = current_datetime
            success = True
            successful_calls += 1  # Increment successful API call counter
        else:
            print(
                f"Attempt {attempts+1}: Failed to fetch API response for {query}")
            attempts += 1

    if not success:
        log_error(ORIGINAL_API_NAME,
                  "API Request Failed After Retries", f"Keyword: {query}")

# Save the updated df_keywords once after processing
df_keywords.to_csv(KEYWORDS_PATH, index=False)
