# API Ninja Data Fetcher Script
#
# This script fetches data from API Ninja APIs for a list of domains,
# saves the responses as JSON files, and logs errors.
#
# Configuration:
# 1. Update CSV_PATH with the path to your API credentials CSV file.
# 2. Update DOMAINS_FILE with the path to your domains Python file.
# 3. Update LOG_PATH with the path to your transaction log directory.
# 4. Ensure API Ninja API credentials are populated in the CSV file.
#
# Requirements:
#   - API Ninja API credentials.
#   - Python 3.x.
#   - requests, pandas, json, and logging libraries.
#
# Usage:
#   1. Run the script.
#   2. The script will fetch data for each domain using API Ninja APIs.
#   3. JSON responses will be saved in the transaction log directory.
#   4. Errors will be logged in the error report CSV file.

import os
import requests
import pandas as pd
import json
import logging
import re
import importlib.util
from datetime import datetime, timedelta


# Get the current file's directory
CURRENT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.join(CURRENT_DIR, '..')


# File paths
CSV_PATH = os.path.join(BASE_DIR, 'Elevator App', 'APIFetchData.csv')
DOMAINS_FILE = os.path.join(
    BASE_DIR, 'Elevator App', 'ANALYSIS_API_Ninja_Domains.py')
LOG_PATH = os.path.join(BASE_DIR, 'API_Ninja_Transaction_Log')
ERROR_LOG_PATH = os.path.join(LOG_PATH, 'error_report.csv')


# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Load domains list from a Python file
def load_domains(file_path):
    spec = importlib.util.spec_from_file_location("domains", file_path)
    domains_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(domains_module)
    return domains_module.unique_display_links_df


# Load API credentials
def load_api_credentials(csv_path):
    return pd.read_csv(csv_path)


# Function to make API requests
def fetch_data(api_url, api_key, domain):
    try:
        if 'dnslookup' in api_url or 'whois' in api_url:
            response = requests.get(
                api_url + domain, headers={'X-Api-Key': api_key})
        else:
            response = requests.get(
                api_url + 'http://' + domain, headers={'X-Api-Key': api_key})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log_error(domain, api_url, str(e))
        return None


# Function to log errors
def log_error(domain, api_url, error_message):
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ERROR_LOG_PATH, 'a') as error_file:
        error_file.write(
            f"{current_timestamp}, Domain: {domain}, API: {api_url}, Error: {error_message}\n")
    logging.error(f"Domain: {domain}, API: {api_url}, Error: {error_message}")


# Function to sanitize file name
def sanitize_file_name(file_name):
    return re.sub(r'[<>:"/\\|?* ]+', '_', file_name)


# Function to check if domain was refreshed in the last 30 days
def domain_refreshed_recently(domain, api_name):
    try:
        files = os.listdir(LOG_PATH)
        # Check files that match the current domain and API
        relevant_files = [f for f in files if domain in f and api_name in f]

        if relevant_files:
            # Find the most recent file and extract the timestamp
            recent_file = sorted(relevant_files, reverse=True)[0]
            timestamp_str = re.search(r'_(\d{14})\.json', recent_file)
            if timestamp_str:
                last_refresh_time = datetime.strptime(
                    timestamp_str.group(1), '%Y%m%d%H%M%S')
                # Check if the last refresh was within the last 30 days
                if datetime.now() - last_refresh_time < timedelta(days=30):
                    return True
        return False
    except Exception as e:
        logging.error(f"Error checking refresh status for {domain}: {str(e)}")
        return False


# Main function
def main():
    domains_df = load_domains(DOMAINS_FILE)
    domains = domains_df['displayLink'].tolist()
    df_api = load_api_credentials(CSV_PATH)

    for domain in domains:
        for _, row in df_api.iterrows():
            api_name = row['API_Name']
            if api_name not in ['API_Ninja_DNS', 'API_Ninja_Who_Is', 'API_Domain_Location']:
                continue  # Skip non-API Ninja APIs

            api_key = row['AddAPI_API_Key']
            api_url = row['AddAPI_URL']

            if api_name == 'API_Ninja_DNS':
                api_url = 'https://api.api-ninjas.com/v1/dnslookup?domain='
            elif api_name == 'API_Ninja_Who_Is':
                api_url = 'https://api.api-ninjas.com/v1/whois?domain='
            elif api_name == 'API_Domain_Location':
                api_url = 'https://api.api-ninjas.com/v1/urllookup?url='

            # Check if the domain was refreshed in the last 30 days
            if domain_refreshed_recently(domain, api_name):
                logging.info(
                    f"Skipping {domain} for {api_name} - recently refreshed.")
                continue

            # Fetch data from API
            json_data = fetch_data(api_url, api_key, domain)
            if json_data:
                file_name = f"{sanitize_file_name(domain)}_{api_name}_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.json"
                try:
                    with open(os.path.join(LOG_PATH, file_name), 'w') as json_file:
                        json.dump(json_data, json_file, indent=4)
                    logging.info(
                        f"Successfully fetched data for {domain} using {api_name}")
                except Exception as e:
                    log_error(domain, api_url,
                              f"Error saving JSON data: {str(e)}")

    logging.info("API data fetching completed.")


if __name__ == "__main__":
    main()
