import os
import requests
from dotenv import dotenv_values

config = dotenv_values('.env')
token = config.get('GITHUB_AUTH_TOKEN')
GRAPHQL_ENDPOINT = 'https://api.github.com/graphql'
headers = {'Authorization': f'Bearer {token}'}


# Function to execute the GraphQL query with pagination
def fetch_data_paged(query, headers, variables):
    has_next_page = True
    while has_next_page:
        json = {'query': query, 'variables': variables}
        response = requests.post(
            GRAPHQL_ENDPOINT, json=json, headers=headers, timeout=10)
        data = response.json()
        if data:
            yield data
        else:
            print("No data found.")
            return

        page_info = data['data']['search']['pageInfo']
        has_next_page = page_info['hasNextPage']
        variables['after'] = page_info['endCursor']


def get_query(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, file_name)

    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


# run the query to retrieve users
variables = {"query": "location:Poland language:TypeScript type:user followers:>100",
             "type": "USER",
             "after": None,
             "perPage": 10}
for page in fetch_data_paged(get_query("search_users.gql"), headers, variables):
    edges = page['data']['search']['edges']
    if edges:
        for edge in edges:
            node = edge['node']
            print(node)
            # print(f"Username: {node['login']}")
            # print(f"Location: {node['location']}\n")

print("No more pages.")

# CREATE TABLE cursors (
#     id SERIAL PRIMARY KEY,
#     end_cursor VARCHAR(255) NOT NULL
# );
