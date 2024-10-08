import os
import json
import zipfile
import pandas as pd
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime
import logging
from oauth2client.service_account import ServiceAccountCredentials


# Get the current file's directory
CURRENT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.join(CURRENT_DIR, '..')


# Set up logging
logging.basicConfig(filename=os.path.join(BASE_DIR, 'backup_log.log'),
                    level=logging.INFO,
                    format="%(asctime)s:%(levelname)s:%(message)s")


# Load API credentials from the CSV file
csv_path = os.path.join(BASE_DIR, 'Elevator App', 'APIFetchData.csv')
api_df = pd.read_csv(csv_path)


# Extract Google Drive API credentials
cloud_api = api_df[api_df['API_Name'] == 'Cloud Backup']
username = cloud_api['AddAPI_Username'].values[0]
password = cloud_api['AddAPI_Password'].values[0]
client_id = cloud_api['AddAPI_API_Key'].values[0]
client_secret = cloud_api['AddAPI_Query'].values[0]
folder_id = cloud_api['AddAPI_URL'].values[0]
# JSON key path from CSV
json_keyfile_path = cloud_api['AddAPI_AdditionalNotesDrop'].values[0]


# Authenticate and set up Google Drive
try:
    scope = ["https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_keyfile_path, scopes=scope)
    gauth = GoogleAuth()
    gauth.credentials = credentials
    drive = GoogleDrive(gauth)
    logging.info("Google Drive authentication successful")
except Exception as e:
    logging.error(f"Google Drive authentication failed: {e}")
    raise


# Load config file
try:
    config_path = os.path.join(BASE_DIR, 'Elevator App', 'config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    logging.error("Config file not found.")
    raise
except json.JSONDecodeError:
    logging.error("Error decoding JSON config file.")
    raise


# Wrapper functions


def zip_project_folder():
    try:
        project_folder = config["project_folder"]
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        zip_file_name = f"PythonTraining_{current_datetime}.zip"

        with zipfile.ZipFile(zip_file_name, "w") as zip_f:
            for root, dirs, files in os.walk(project_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_f.write(file_path, os.path.relpath(
                        file_path, project_folder))

        logging.info(f"Project folder zipped: {zip_file_name}")
        return zip_file_name
    except Exception as e:
        logging.error(f"Failed to zip project folder: {e}")
        raise


def backup_to_cloud(zip_file):
    try:
        # Create a new file in Google Drive
        gfile = drive.CreateFile({'parents': [{'id': folder_id}]})
        gfile.SetContentFile(zip_file)
        gfile.Upload()  # Upload the file
        logging.info(f"Backup uploaded to Google Drive: {zip_file}")
    except Exception as e:
        logging.error(f"Failed to upload backup to Google Drive: {e}")
        raise


def run_backup():
    try:
        # Zip project folder
        zip_file = zip_project_folder()

        # Upload to Google Drive
        backup_to_cloud(zip_file)

        print(f"Backup completed: {zip_file}")
        logging.info(f"Backup completed successfully: {zip_file}")
    except Exception as e:
        logging.error(f"Backup process failed: {e}")
        print(f"Backup failed: {e}")


# Run backup
run_backup()
