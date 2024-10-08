**Elevator App**
================

Elevator App is a proprietary Python-based application designed to facilitate keyword-based Google searches and track intellectual property (IP) infringements using the Google Search API. Additionally, the app leverages API Ninja to retrieve DNS, WHOIS, and domain location information, streamlining the process of filing DMCA takedown notices.


**Note on Code Availability**
---------------------------
As Elevator App is a commercial project, this repository provides selective code snippets demonstrating API functionality while withholding the overall design and architecture of the application's proof-of-concept (POC). Access to the complete codebase is restricted.


**Functionality Overview**
-------------------------

* Keyword-based Google search scheduling
* Intellectual property (IP) infringement tracking
* DNS, WHOIS, and domain location information retrieval via API Ninja
* DMCA takedown notice assistance


**Status**
----------

Under development. For more information, please contact [shaun.hardrick@gmail.com]. 
## Features

- **GSTEXT Management**: Automatically generate Google Search keywords based on user-inputted department fields and subtext keywords.
- **Pirate Tracker**: Track unauthorized use of intellectual property by collecting information from WHOIS, DNS, and domain location services.
- **API Fetching**: Automate API queries to Google Search API and API Ninja for keyword-based searches and domain data retrieval.
- **Dynamic Scheduling**: Schedule and automate the execution of Python scripts using a CSV-based system.
- **Unshorten URLs**: Use Python’s `unshorten` library to reveal full URLs returned by the Google Search API.
- **Backup System**: Automated Google Drive backup to secure project data and logs.
  
## Current Functionalities (Phase 1)

- **GSTEXT Keyword Generation**: Allows users to generate and manage keyword lists efficiently.
- **API Fetcher**: Enables scheduled fetches of domain data from Google Search API and API Ninja, with error logging for troubleshooting.
- **Dynamic Script Scheduling**: Automates script execution based on priorities and schedules, facilitating seamless data refreshes for Tableau dashboards.
- **Backup Mechanism**: Daily automated backups to Google Drive using the Google Drive API, ensuring data integrity and disaster recovery.
  
## Planned Enhancements (Phase 2 and Beyond)

- **Tableau Dashboard**: Visualize parsed data (WHOIS, DNS, Domain Location) on interactive dashboards for IP tracking and monitoring.
- **User Management**: Add secure user authentication and company information management using bcrypt and pandas.
- **MySQL Integration**: Transition from CSV-based data storage to a MySQL database for improved scalability and performance.
- **Web Interface**: Develop a user-friendly web application for managing keyword lists, viewing IP infringements, and generating reports.
- **Automated API Key Rotation**: Automate API key management to avoid exceeding API rate limits and ensure data fetch continuity.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/ElevatorApp.git
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your configuration files for API credentials:
   - Place your `APIFetchData.csv` file in the `config` folder.
   - Add your Google Drive API credentials (JSON) to the same folder.

4. Update the `config.json` file to specify your project paths and Google API keys.

## Usage

- **Dynamic Scheduling**: The system will automatically run scripts in the correct order based on their priority in the CSV file. To manually run a script:
    ```bash
    python script_name.py
    ```

- **API Fetching**: To fetch Google Search or API Ninja data for your keywords:
    ```bash
    python FETCHgoogleSearchAPI.py
    python FETCHapininja.py
    ```

- **Backup**: To manually trigger a backup to Google Drive:
    ```bash
    python 000BackupToGoogleDrive.py

    ## Setting Up API Credentials

To use the API fetching features of the Elevator App (Google Search API, API Ninja), you'll need to store your API credentials in the `APIFetchData.csv` file. This file should include columns for API Name, API Key, Username, and Password.

While the `Add API Fetch Credentials` script is not included in the repository due to security reasons, here is how it works:

1. **Add API Fetch Credentials**: 
   - This script allows users to add and store API credentials (Google Search, API Ninja) by collecting input like API name, username, password, and API key.
   - The credentials are stored securely in the `APIFetchData.csv` file, which is referenced by the API-fetching scripts.

Ensure your `APIFetchData.csv` contains the following columns:
- **API_Name**: Name of the API (e.g., Google Search API, API Ninja)
- **API_Key**: Your unique API key
- **Username**: Username associated with the API (if applicable)
- **Password**: Password for the API (if applicable)

> Note: This file should be kept locally and never pushed to GitHub to protect your credentials.

    ```

## Folder Structure

