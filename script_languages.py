import requests
import pandas as pd
import pymongo
import time

# colocar token aqui
token = "eOVIR7AwkNb7mzKjuY4UoGSqedkBkL0dC4nu"

headers = {"Authorization": "bearer ghp_"+token}

query = """
{
  search(query: "author:userlogin is:pr", type: ISSUE, first: 10, after: null) {
    issueCount
    pageInfo {
      endCursor
      startCursor
    }
    nodes {
      ... on PullRequest {
        commits(first: 100) {
            nodes {
                commit {
                    tree {
                        entries {
                            language {
                                id 
                                name
                            }
                        }
                    }
                }
            }
        }
      }
    }
  }
}
"""
# files(first: 100) {
#     totalCount
#     nodes {
#     path
#     }
# }

# le usuarios do mongo

connection_string = f"mongodb+srv://pvfcosta:dsh2023.retorno@ti6-lbtqia-research.bdfqdy0.mongodb.net/test"

client = pymongo.MongoClient(connection_string)

mydb = client['ti-data']

user_collection = "users_no_duplicates"
language_collection = "languages"
user_language_collection = "usersLanguages"
user_conn_collection = mydb[user_collection]


userLogin = "userlogin"
# endCursor = "null"
# language = { 'id', 'name', 'color'}


# usersLanguage = {'userId', 'languageId'}

# pega todos os usuarios do mongo
users = list(user_conn_collection.find({}).sort('login', pymongo.ASCENDING))

if language_collection in mydb.list_collection_names():
    print("The language collection exists.")
    lang_conn_collection = mydb[language_collection]
else:
    lang_conn_collection = mydb.create_collection(language_collection)

if user_language_collection in mydb.list_collection_names():
    print("The users languages collection exists.")
    usrlang_conn_collection = mydb[user_language_collection]
else:
    usrlang_conn_collection = mydb.create_collection(user_language_collection)

usersLanguages = list(usrlang_conn_collection.find(
    {}).sort('login', pymongo.ASCENDING))

allLanguages = list(lang_conn_collection.find({}))

if len(usersLanguages) > 0:
    lastUser = usersLanguages[len(usersLanguages) - 1]
else:
    lastUser = {}

for user in users:
    if lastUser != {} and lastUser['userLogin'] != user['login']:
        continue
    # finduser = list(usrlang_conn_collection.find(
    #                                 {"userLogin": user['login']}))
    # if len(finduser) > 0:
    #     continue
    error = 0
    endCursor = "null"
    query_language = query
    query_language = query_language.replace(userLogin,
                                            user['login'])
    # pega todos os arquivos alterados em todos os prs
    while True:
        request = requests.post('https://api.github.com/graphql',
                                json={'query': query_language}, headers=headers)
        resultLanguage = request.json()

        if 'data' in resultLanguage and resultLanguage['data'] is not None:
            allPrs = resultLanguage['data']['search']['nodes']
            for pr in allPrs:
                if 'nodes' in pr['commits']:
                    prCommits = pr['commits']['nodes']
                    for commit in prCommits:
                        entries = commit['commit']['tree']['entries']
                        for entrie in entries:
                            if entrie['language'] is not None:
                                findLanguages = list(lang_conn_collection.find(
                                    {"id": entrie['language']['id'], "name": entrie['language']['name']}))
                                if len(findLanguages) == 0:
                                    pushedLanguage = lang_conn_collection.insert_one(
                                        entrie['language'])
                                    allLanguages.append(pushedLanguage)
                                userLanguage = {
                                    'languageId': entrie['language']['id'], 'userLogin': user['login']}
                                findusersLanguages = list(usrlang_conn_collection.find(
                                    {"languageId": entrie['language']['id'], "userLogin": user['login']}))
                                if len(findusersLanguages) == 0:
                                    pushedUserLanguage = usrlang_conn_collection.insert_one(
                                        userLanguage)
                                    usersLanguages.append(pushedUserLanguage)
            print(resultLanguage['data']['search']['pageInfo']['endCursor'])
            if resultLanguage['data']['search']['pageInfo']['endCursor'] == None:
                break
            query_language = query_language.replace(endCursor, '"'+resultLanguage['data']
                                                    ['search']['pageInfo']['endCursor']+'"')
            endCursor = '"' + \
                resultLanguage['data']['search']['pageInfo']['endCursor']+'"'
        else:
            # break
            print('error')
            error += 1
            time.sleep(5)
            if (error > 5):
                print("Error na chamada da api do git hub")
                print(resultLanguage)
                break
            else:
                pass
    lastUser = {}
    # print(usersLanguages)

# dfLanguages = pd.DataFrame(allLanguages)
# dfLanguages.to_csv('allLanguages.csv', index=False, sep=';', encoding='utf-8')

# dfusersLanguages = pd.DataFrame(usersLanguages)
# dfusersLanguages.to_csv('usersLanguages.csv',
#                         index=False, sep=';', encoding='utf-8')
