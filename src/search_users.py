import os
import requests
from dotenv import dotenv_values

config = dotenv_values('.env')
token = config.get('GITHUB_AUTH_TOKEN')
url = 'https://api.github.com/graphql'
headers = {'Authorization': f'Bearer {token}'}


# Function to execute the GraphQL query with pagination
def fetch_data(query, headers, variables, extract_data):
    has_next_page = True
    while has_next_page:
        response = requests.post(
            url, json={'query': query, 'variables': variables}, headers=headers, timeout=10)
        data = response.json()
        extracted_data = extract_data(data)
        if extracted_data:
            yield from extracted_data
        else:
            print("No data found.")
            return

        page_info = data['data']['search']['pageInfo']
        has_next_page = page_info['hasNextPage']
        variables['after'] = page_info['endCursor']


# Function to extract user data from the response
def extract_users(data):
    edges = data['data']['search']['edges']
    if edges:
        for edge in edges:
            node = edge['node']
            yield node
    else:
        return


# read the query from the file
dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, 'search_users.gql')

with open(file_path, 'r', encoding='utf-8') as file:
    getSearchResultsQuery = file.read()

# run the query to retrieve users
variables = {"query": "location:Poland language:TypeScript type:user followers:>100",
             "type": "USER",
             "after": None,
             "perPage": 10}
for user in fetch_data(getSearchResultsQuery, headers, variables, extract_users):
    print(f"Username: {user['login']}")
    print(f"Location: {user['location']}\n")

# Run the query to retrieve repositories
# searchType = "REPOSITORY"
# variables = {"searchQuery": searchQuery, "searchType": searchType, "after": after_cursor, "perPage": 10}
# for repo in fetch_data(getSearchResultsQuery, headers, variables, extract_repos):
#     print(f"Repository Name: {repo['name']}")
#     print(f"Description: {repo['description']}\n")


print("No more pages.")
