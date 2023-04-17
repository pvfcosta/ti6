
import requests
import pandas as pd
import matplotlib.pyplot as plot
import pymongo

connection_string = f"mongodb+srv://pvfcosta:dsh2023.retorno@ti6-lbtqia-research.bdfqdy0.mongodb.net/test"

client = pymongo.MongoClient(connection_string)

mydb = client['ti-data']

# colocar token aqui
token = "KM4r0WcRDdbDewRvZ71dMEjG0kLky543xsx6"

headers = {"Authorization": "bearer ghp_"+token}

allResults = []
allWordsResults = []
allOrganizations = []

words = ["queer", "rainbow_flag", "transgender_flag", "nonbinary", "non binary", "lesbian",
         "bisexual", "asexual", "pansexual", "transgender", "they them", "he them", "she them"]
# "gay", "rainbow, "trans",

query = """
{
  search(query:" term in:fullName type:user", type: USER, first: 30, after:null) {
    userCount
    pageInfo {
      endCursor
      startCursor
    }
    nodes {
      ... on User {
        login
        name
        bio
        bioHTML
        url
        pronouns
        createdAt
        status {
          emoji
        }
        organizations(first: 17) {
          totalCount
          edges {
            node {
              url
              name
              isVerified
            }
          }
        }
      }
    }
  }
}
"""
term = "term"

error = 0
i = 0
for word in words:
    query = query.replace(term, word)
    term = word
    if i > 0:
        query = query.replace(endCursor, "null")
    endCursor = "null"
    i += 1

    while True:
        request = requests.post('https://api.github.com/graphql',
                                json={'query': query}, headers=headers)
        result = request.json()
        if 'data' in result:
            allResults += result['data']['search']['nodes']

            # logica pra separar por aba da tabela
            for node in result['data']['search']['nodes']:
              wordResults = {
                  'search': word,
                  'login': node['login'],
                  'name': node['name'],
                  'bio': node['bio'],
                  'bioHTML': node['bioHTML'],
                  'url': node['url'],
                  'pronouns': node['pronouns'],
                  'createdAt': node['createdAt'],
                  'status': node['status'],
                  'organizations': node['organizations']['totalCount']
              }
              allWordsResults.append(wordResults)

                # itera sobre organizacoes dos usuarios
              for org in node['organizations']['edges']:
                if org['node'] is not None:
                    allOrganizations.append(org['node'])

            print(result['data']['search']['pageInfo']['endCursor'])
            if result['data']['search']['pageInfo']['endCursor'] == None:
                break
            query = query.replace(endCursor, '"'+result['data']
                                  ['search']['pageInfo']['endCursor']+'"')
            endCursor = '"' + \
                result['data']['search']['pageInfo']['endCursor']+'"'
        else:
            # break
            error += 1
            if (error > 5):
                print("Error na chamada da api do git hub")
                print(result)
                break
            else:
                pass

org_collection = "organizations"
user_collection = "users"

if org_collection in mydb.list_collection_names():
  print("The collection exists.")
  org_conn_collection = mydb[org_collection]
else:
  org_conn_collection = mydb.create_collection(org_collection)

org_conn_collection.insert_many(allOrganizations)

if user_collection in mydb.list_collection_names():
  print("The collection exists.")
  user_conn_collection = mydb[user_collection]
else:
  user_conn_collection = mydb.create_collection(user_collection)

user_conn_collection.insert_many(allWordsResults)