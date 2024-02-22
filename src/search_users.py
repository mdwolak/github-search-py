import json
import os
import requests
from dotenv import dotenv_values
from db import Database  # pylint: disable=E0401


config = dotenv_values('.env')
token = config.get('GITHUB_AUTH_TOKEN')
GRAPHQL_ENDPOINT = 'https://api.github.com/graphql'
HEADERS = {'Authorization': f'Bearer {token}'}


# Function to execute the GraphQL query with pagination
def fetch_data_paged(query, headers, variables):
    has_next_page = True
    while has_next_page:
        request_json = {'query': query, 'variables': variables}
        response = requests.post(
            GRAPHQL_ENDPOINT, json=request_json, headers=headers, timeout=10)
        data = response.json()
        if data:
            page_info = data['data']['search']['pageInfo']
            has_next_page = page_info['hasNextPage']
            variables['after'] = page_info['endCursor']

            yield data, page_info['endCursor']
        else:
            print("No data found.")
            return


def get_query(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, file_name)

    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def print_users(edges):
    if edges:
        for edge in edges:
            print(edge)
            # print(f"Username: {node['login']}")
            # print(f"Location: {node['location']}\n")


def download_data():
    # run the query to retrieve users
    variables = {"query": "location:Poland language:TypeScript type:user followers:>100",
                 "type": "USER",
                         "after": None,
                         "perPage": 10}

    db = Database()

    load_id = db.data_load_start(
        "github.users.search", variables['query'])
    page_index = 0

    try:
        for page, cursor in fetch_data_paged(get_query("search_users.gql"), HEADERS, variables):
            users = page['data']['search']['items']
            db.data_page_insert(load_id, page_index, cursor, json.dumps(users))
            page_index += 1
            print_users(users)
            print(f"Cursor position: {cursor}")
    except Exception as e:  # pylint: disable=W0718
        db.data_load_finish(load_id, page_index, str(e))
    else:
        db.data_load_finish(load_id, page_index)

    print("No more pages.")


download_data()
