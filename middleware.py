import os
import requests
from requests.auth import HTTPBasicAuth
import json
import time
# Probably import logging of sorts

# Setup logging
# adding comment to file for PR test


# Dynamically load configuration from environment variables
jira_instances = [
    {
        'url': os.getenv('JIRA_URL_1', 'https://default-jira-instance-1.atlassian.net'),
        'username': os.getenv('JIRA_USERNAME_1', 'default-email-1@example.com'),
        'api_token': os.getenv('JIRA_API_TOKEN_1', 'default-api-token-1')
    },
    {
        'url': os.getenv('JIRA_URL_2', 'https://default-jira-instance-2.atlassian.net'),
        'username': os.getenv('JIRA_USERNAME_2', 'default-email-2@example.com'),
        'api_token': os.getenv('JIRA_API_TOKEN_2', 'default-api-token-2')
    }
]

# Load LinearB API configuration from environment variables
linearb_url = os.getenv('LINEARB_API_URL', 'https://api.linearb.io/default-endpoint')
linearb_api_key = os.getenv('LINEARB_API_KEY', 'default-linearb-api-key')

# Dynamically load project key from environment variables
project_key = os.getenv('JIRA_PROJECT_KEY', 'default_project_key')

# Fetch data from Jira
def fetch_jira_data(jira_instance):
    url = f"{jira_instance['url']}/rest/api/3/search"
    headers = {
        'Accept': 'application/json'
    }
    query = {
        'jql': f'project = {project_key}'
    }
    try:
        response = requests.get(url, headers=headers, params=query, auth=HTTPBasicAuth(jira_instance['username'], jira_instance['api_token']))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP error occurred when fetching data from {jira_instance['url']}: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Error connecting to {jira_instance['url']}: {errc}")
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout error occurred when fetching data from {jira_instance['url']}: {errt}")
    except requests.exceptions.RequestException as err:
        logger.error(f"An error occurred when fetching data from {jira_instance['url']}: {err}")
    return None

# Consolidate data from multiple Jiras
def consolidate_data(jira_data_list):
    consolidated_data = []
    for jira_data in jira_data_list:
        for issue in jira_data['issues']:
            consolidated_issue = {
                'id': issue['id'],
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'status': issue['fields']['status']['name']
            }
            consolidated_data.append(consolidated_issue)
    return consolidated_data

# Send data to LinearB
def send_data_to_linearb(data):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {linearb_api_key}"
    }
    try:
        response = requests.post(linearb_url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        logger.info("Data sent successfully to LinearB")
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP error occurred when sending data to LinearB: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Error connecting to LinearB: {errc}")
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout error occurred when sending data to LinearB: {errt}")
    except requests.exceptions.RequestException as err:
        logger.error(f"An error occurred when sending data to LinearB: {err}")

# Main execution flow (exmaple)
def main():
    jira_data_list = []
    for jira_instance in jira_instances:
        data = fetch_jira_data(jira_instance)
        if data:
            jira_data_list.append(data)
        time.sleep(1)  # To avoid hitting Jira API rate limits

    if jira_data_list:
        consolidated_data = consolidate_data(jira_data_list)
        send_data_to_linearb(consolidated_data)
    else:
        logger.warning("No data was fetched from Jira instances. Nothing to send to LinearB.")

if __name__ == "__main__":
    main()

