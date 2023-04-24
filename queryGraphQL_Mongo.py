
import requests
import pandas as pd
import matplotlib.pyplot as plot
import datetime
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
membersColumn = []

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
        id
        databaseId
        email
        login
        name
        bio
        bioHTML
        url
        pronouns
        createdAt
        location
        status {
          emoji
        }
        pullRequests {
          totalCount
        }
        issues {
          totalCount
        }
        organizations(first: 17) {
          totalCount
          edges {
            node {
              url
              name
              isVerified
              repositories(first: 1, privacy: PUBLIC) {
                totalCount
              }
              membersWithRole {
                totalCount
              }
            }
          }
        }
        contributionsCollection {
          totalCommitContributions
          startedAt
          endedAt
        }
        followers {
          totalCount
        }
        following {
          totalCount
        }
        sponsors {
          totalCount
        }
        sponsoring {
          totalCount
        }
      }
    }
  }
}
"""
term = "term"

error = 0
i = 0

today = datetime.datetime.utcnow()
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
        if 'data' in result and result['data'] is not None:
            allResults += result['data']['search']['nodes']

            # logica pra separar por aba da tabela
            for node in result['data']['search']['nodes']:
              createdAt = datetime.datetime.strptime(
                    node['createdAt'], '%Y-%m-%dT%H:%M:%SZ')
              accountAgeInDays = today - createdAt

              # calcula frequencia de commits
              commitsStartedAt = datetime.datetime.strptime(
                  node['contributionsCollection']['startedAt'], '%Y-%m-%dT%H:%M:%SZ')
              commitsEndedAt = datetime.datetime.strptime(
                  node['contributionsCollection']['endedAt'], '%Y-%m-%dT%H:%M:%SZ')
              contributionTime = commitsEndedAt - commitsStartedAt
              commitsPerWeek = node['contributionsCollection']['totalCommitContributions'] / ( contributionTime.days / 7 )

              wordResults = {
                  'search': word,
                  'login': node['login'],
                  'name': node['name'],
                  'bio': node['bio'],
                  'bioHTML': node['bioHTML'],
                  'url': node['url'],
                  'pronouns': node['pronouns'],
                  'createdAt': createdAt,
                  'status': node['status'],
                  'organizations': node['organizations']['totalCount'],
                  'location': node['location'],
                  'pullRequests':node['pullRequests']['totalCount'],
                  'issues':node['issues']['totalCount'],
                  'organizations':node['organizations']['totalCount'],
                  'totalCommitContributions':node['contributionsCollection']['totalCommitContributions'],
                  'commitsStartedAt':node['contributionsCollection']['startedAt'],
                  'commitsEndedAt':node['contributionsCollection']['endedAt'],
                  'accountAge':accountAgeInDays.days,
                  'followers':node['followers']['totalCount'],
                  'following':node['following']['totalCount'],
                  'sponsors':node['sponsors']['totalCount'],
                  'sponsoring':node['sponsoring']['totalCount'],
                  'commitsPerWeek':commitsPerWeek
              }
              allWordsResults.append(wordResults)

                # itera sobre organizacoes dos usuarios
              for org in node['organizations']['edges']:
                    if org['node'] is not None:
                        org['node']['repositories'] = org['node']['repositories']['totalCount']   
                        org['node']['membersWithRole'] = org['node']['membersWithRole']['totalCount']                    
                        if org['node'] in allOrganizations:
                            indice = allOrganizations.index(org['node'])
                            membersColumn[indice] += 1 
                        else:
                            allOrganizations.append(org['node'])
                            membersColumn.append(1)

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