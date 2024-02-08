from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from dotenv import dotenv_values

config = dotenv_values('.env')
token = config.get('GITHUB_AUTH_TOKEN')


def get_users():
    url = 'https://api.github.com/graphql'
    headers = {
        'Authorization': f'Bearer {token}'
    }

    transport = RequestsHTTPTransport(url=url, headers=headers)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql('''
        query {
            search(query: "location:Poland language:Typescript", type: USER, first: 100) {
                nodes {
                    ... on User {
                        login
                    }
                }
            }
        }
    ''')

    response = client.execute(query)
    if 'errors' not in response:
        items = response['data']['search']['nodes']
        return items
    else:
        return None


users = get_users()
if users:
    for user in users:
        print(user['login'])
else:
    print('Failed to retrieve users from GitHub.')
