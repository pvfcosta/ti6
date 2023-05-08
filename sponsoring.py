
import requests
import pymongo
import time

connection_string = f"mongodb+srv://pvfcosta:dsh2023.retorno@ti6-lbtqia-research.bdfqdy0.mongodb.net/test"

client = pymongo.MongoClient(connection_string)

mydb = client['ti-data']

GITHUB_API_ENDPOINT = "https://api.github.com/graphql"

NUMBER_OF_ATTEMPTS = 15

# colocar token aqui
token = "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"

CURSOR_QUERY = """
query($login:String!,$cursor:String!)
{
  user(login: $login) {
    sponsoring(after: $cursor, first: 50) {
      nodes {
        ... on User { login }
        ... on Organization { login }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
"""

INITIAL_QUERY = """
query($login:String!)
{
  user(login: $login) {
    sponsoring(after: null, first: 50) {
      nodes {
        ... on User { login }
        ... on Organization { login }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
"""

user_collection = "users"

if user_collection in mydb.list_collection_names():
  user_conn_collection = mydb[user_collection]
else:
    print("The collection doesn't exist.")

sponsor_collection = "sponsor"

if sponsor_collection in mydb.list_collection_names():
  print("The collection exists.")
  foll_conn_collection = mydb[sponsor_collection]
else:
  foll_conn_collection = mydb.create_collection(sponsor_collection)

def run_query_variables(query, attemp, variables):

        headers = {"Authorization": "Bearer " + token}

        request = requests.post(GITHUB_API_ENDPOINT, headers=headers, json={"query": query, "variables": variables})

        if request.status_code == 200:
            return request.json()
        elif attemp <= NUMBER_OF_ATTEMPTS:
            print("Tentativa de conexão falhou :(. {}/{} Tentando novamente...".format(attemp,
                  NUMBER_OF_ATTEMPTS))
            time.sleep(1)
            return run_query_variables(query, attemp + 1, variables)
        else:
            raise Exception("Tentativa de conexão falhou com o erro: {}. {}".format(
                request.status_code, query))

def save_sponsoring(login, sponsoring):
    data = []
    for sp in sponsoring:
        sponsor = {
            "sponsor": sp["login"],
            "sponsoring": login
        }
        data.append(sponsor)

    if len(data) > 0:
        foll_conn_collection.insert_many(data)
    else:
        print("No data to be inserted")


def fetch_sponsoring(login):
    variables = {"login": login}
    has_next = True
    i = 0
    end_cursor = "null"
    sponsors = []
    query = INITIAL_QUERY

    response = run_query_variables(query, 1, variables)

    sponsors += response["data"]["user"]["sponsoring"]["nodes"]

    has_next = response["data"]["user"]["sponsoring"]["pageInfo"]["hasNextPage"]

    if has_next:
        end_cursor = response["data"]["user"]["sponsoring"]["pageInfo"]["endCursor"]

    i += 1

    query = CURSOR_QUERY

    while(has_next):

        variables = {"login": login,"cursor":end_cursor}

        response = run_query_variables(query, 1, variables)

        has_next = response["data"]["user"]["sponsoring"]["pageInfo"]["hasNextPage"]

        if has_next:
            end_cursor = response["data"]["user"]["sponsoring"]["pageInfo"]["endCursor"]

        sponsors += response["data"]["user"]["sponsoring"]["nodes"]

        print(end_cursor)

        i += 1

    save_sponsoring(login, sponsors)

cursor = user_conn_collection.find({})    

for document in cursor:
    login = document['login']
    print('usuario: ' + login)
    fetch_sponsoring(login)

print('Done!')