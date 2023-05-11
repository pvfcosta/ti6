
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
token_1 = "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"

token_2 = "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"

token = token_2

allResults = []
allWordsResults = []
allRepositories = []
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
  {'keyword': "gay", 'has_filter': True},
  {'keyword': "trans", 'has_filter': True},
  {'keyword': "transboy", 'has_filter': False},
  {'keyword': "transgirl", 'has_filter': False},
  {'keyword': "transwoman", 'has_filter': False},
  {'keyword': "transmen", 'has_filter': False},
  ]
# "gay", "rainbow, "trans",

query = """
{
  search(query:"term in:fullName", type: USER, first: 10, after:null) {
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
        repositories {
          totalCount
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
user_collection = "users"

if user_collection in mydb.list_collection_names():
  print("The collection exists.")
  user_conn_collection = mydb[user_collection]
else:
  user_conn_collection = mydb.create_collection(user_collection)

user_cursor = user_conn_collection.find()

user_df = pd.DataFrame(list(user_cursor))

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
      headers = {"Authorization": "bearer "+token}
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
            repo_total_count = node['repositories']['totalCount']

            if len(user_df) > 0 and login in user_df['login'].to_list():
              print('already exists')
              continue
            if word['has_filter']:
              spaced_word = ' ' + keyword + ' '
              spaced_word_1 = keyword + ' '
              spaced_word_2 = ' ' + keyword
              print(spaced_word)
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
                'repositories': node['repositories']['totalCount'],
                'location': node['location'],
                'pullRequests':node['pullRequests']['totalCount'],
                'issues':node['issues']['totalCount'],
                'repositories':repo_total_count,
                'totalCommitContributions':node['contributionsCollection']['totalCommitContributions'],
                'commitsStartedAt':node['contributionsCollection']['startedAt'],
                'commitsEndedAt':node['contributionsCollection']['endedAt'],
                'accountAge':accountAgeInDays.total_seconds()/3600*24*365,
                'followers':node['followers']['totalCount'],
                'following':node['following']['totalCount'],
                'sponsors':node['sponsors']['totalCount'],
                'sponsoring':node['sponsoring']['totalCount'],
                'commitsPerWeek':commitsPerWeek
            }
                                  
            user_conn_collection.insert_one(wordResults)

          #print(result['data']['search']['pageInfo']['endCursor'])
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