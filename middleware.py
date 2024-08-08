import requests
from requests.auth import HTTPBasicAuth
import json
import time

# Jira instance details
jira_instances = [
    {
        'url': 'https://your-jira-instance-1.atlassian.net',
        'username': 'your-email-1@example.com',
        'api_token': 'your-api-token-1'
    },
    {
        'url': 'https://your-jira-instance-2.atlassian.net',
        'username': 'your-email-2@example.com',
        'api_token': 'your-api-token-2'
    }
]

# Function to fetch data from Jira
def fetch_jira_data(jira_instance):
    url = f"{jira_instance['url']}/rest/api/3/search"
    headers = {
        'Accept': 'application/json'
    }
    query = {
        'jql': 'project = YOUR_PROJECT_KEY'
    }
    response = requests.get(url, headers=headers, params=query, auth=HTTPBasicAuth(jira_instance['username'], jira_instance['api_token']))
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from {jira_instance['url']}: {response.status_code}")
        return None

# Fetch data from all Jira instances
jira_data_list = []
for jira_instance in jira_instances:
    data = fetch_jira_data(jira_instance)
    if data:
        jira_data_list.append(data)
    time.sleep(1)  # To avoid hitting rate limits

# Function to consolidate data
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

# Consolidate data
consolidated_data = consolidate_data(jira_data_list)

# LinearB API details
linearb_url = 'https://api.linearb.io/your-endpoint'
linearb_api_key = 'your-linearb-api-key'

# Function to send data to LinearB
def send_data_to_linearb(data):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {linearb_api_key}"
    }
    response = requests.post(linearb_url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("Data sent successfully to LinearB")
    else:
        print(f"Failed to send data to LinearB: {response.status_code}")

# Send consolidated data to LinearB
send_data_to_linearb(consolidated_data)
