
import requests
import pandas as pd
import matplotlib.pyplot as plot
import datetime
import pymongo
from time import sleep

connection_string = f"mongodb+srv://pvfcosta:dsh2023.retorno@ti6-lbtqia-research.bdfqdy0.mongodb.net/test"

client = pymongo.MongoClient(connection_string)

mydb = client['ti-data']

# colocar token aqui
token_1 = "h6fUn0ZzrGBw2G8BwccjPbQmin1nw54gdMK8"

token_2 = "P3gX7jsmqOK4zeG3F9nj4FgAGm1lP41JRj4R"

token = token_1

allResults = []
allWordsResults = []
allOrganizations = []
membersColumn = []

words = [
  {'keyword': "queer", 'has_filter': False}, 
  {'keyword': "rainbow_flag", 'has_filter': False},
  {'keyword': "transgender_flag", 'has_filter': False},
  {'keyword': "nonbinary", 'has_filter': False},
  {'keyword': "non binary", 'has_filter': False},
  {'keyword': "lesbian", 'has_filter': False},
  {'keyword':"bisexual", 'has_filter': False},
  {'keyword': "asexual", 'has_filter': False},
  {'keyword': "pansexual", 'has_filter': False},
  {'keyword': "transgender", 'has_filter': False},
  {'keyword': "they them", 'has_filter': False},
  {'keyword': "he them", 'has_filter': False},
  {'keyword': "she them", 'has_filter': False},
  {'keyword': "gay", 'has_filter': True}
  ]
# "gay", "rainbow, "trans",

query = """
{
  search(query:" term in:fullName", type: USER, first: 10, after:null) {
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
org_collection = "organizations"
user_collection = "users"

if org_collection in mydb.list_collection_names():
  print("The collection exists.")
  org_conn_collection = mydb[org_collection]
else:
  org_conn_collection = mydb.create_collection(org_collection)

if user_collection in mydb.list_collection_names():
  print("The collection exists.")
  user_conn_collection = mydb[user_collection]
else:
  user_conn_collection = mydb.create_collection(user_collection)

user_cursor = user_conn_collection.find()

org_cursor = org_conn_collection.find()

user_df = pd.DataFrame(list(user_cursor))

org_df = pd.DataFrame(list(org_cursor))

term = "term"

error = 0
i = 0

today = datetime.datetime.utcnow()
for word in words:
    keyword = word['keyword']
    query = query.replace(term, keyword)
    term = keyword
    if i > 0:
        query = query.replace(endCursor, "null")
    endCursor = "null"
    i += 1

    while True:
      headers = {"Authorization": "bearer ghp_"+token}
      try:
        request = requests.post('https://api.github.com/graphql',
                                json={'query': query}, headers=headers)
      except:
        request = requests.post('https://api.github.com/graphql',
                                json={'query': query}, headers=headers)
                                
      result = request.json()
      if 'data' in result and result['data'] is not None:
          allResults += result['data']['search']['nodes']

          # logica pra separar por aba da tabela
          for node in result['data']['search']['nodes']:
            if len(node) == 0:
              continue
            login = node['login']
            body = node['bio']
            body_html = node['bioHTML']
            status = node['status']
            org_total_count = node['organizations']['totalCount']

            if len(user_df) > 0 and login in user_df['login'].to_list():
              print('already exists')
              continue
            if word['has_filter']:
              spaced_word = ' ' + keyword + ' '
              spaced_word_1 = keyword + ' '
              spaced_word_2 = ' ' + keyword
              if status is None:
                status = ''
              if body is None:
                body = ''
              if body_html is None:
                body_html = ''
              body_condition = spaced_word in body or spaced_word_1 in body or spaced_word_2 in body
              bodyHtml_condition = spaced_word in body_html or spaced_word_1 in body_html or spaced_word_2 in body_html
              status_condition = spaced_word in status or spaced_word_1 in status or spaced_word_2 in status
              if not(body_condition or bodyHtml_condition or status_condition):
                print('continue')
                continue


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
                'search': keyword,
                'login': login,
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
                'organizations':org_total_count,
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
                          
            user_conn_collection.insert_one(wordResults)
            if int(org_total_count) > 0:
              org_conn_collection.insert_many(allOrganizations)
              allOrganizations = []

          print(result['data']['search']['pageInfo']['endCursor'])
          if result['data']['search']['pageInfo']['endCursor'] == None:
              break
          query = query.replace(endCursor, '"'+result['data']
                                ['search']['pageInfo']['endCursor']+'"')
          endCursor = '"' + \
              result['data']['search']['pageInfo']['endCursor']+'"'
      else:
        print('sleep')
        sleep(1)
        if token == token_1:
          token = token_2
        else:
          token = token_1
          # break
        error += 1
        if (error > 5):
            print("Error na chamada da api do git hub")
            print(result)
            break
        else:
            pass