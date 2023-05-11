
import requests
import pandas as pd
import matplotlib.pyplot as plot
import pymongo
import datetime
from time import sleep

connection_string = f"mongodb+srv://pvfcosta:dsh2023.retorno@ti6-lbtqia-research.bdfqdy0.mongodb.net/test"

client = pymongo.MongoClient(connection_string)

mydb = client['ti-data']

GITHUB_API_ENDPOINT = "https://api.github.com/graphql"

NUMBER_OF_ATTEMPTS = 15

# colocar token aqui

CURSOR_QUERY = """
query($login:String!,$cursor:String!)
{
  user(login: $login) {
    repositories(first: 50, after:$cursor) {
      nodes {
        nameWithOwner
        createdAt
        stargazerCount
        primaryLanguage {
          name
        }
        totalIssues: issues {
          totalCount
        }
        closedIssues: issues(states: CLOSED) {
          totalCount
        }
        pullRequests {
          totalCount
        }
        owner {
          ... on Organization {
            membersWithRole {
              totalCount
            }
            name
          }
        }
        totalCommitCount: defaultBranchRef {
          target {
            ... on Commit {
              history(first: 1) {
                totalCount
                nodes {
                  committedDate
                }
              }
            }
          }
        }
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
    repositories(first: 50, after:null) {
      nodes {
        nameWithOwner
        createdAt
        stargazerCount
        primaryLanguage {
          name
        }
        totalIssues: issues {
          totalCount
        }
        closedIssues: issues(states: CLOSED) {
          totalCount
        }
        pullRequests {
          totalCount
        }
        owner {
          ... on Organization {
            membersWithRole {
              totalCount
            }
            name
          }
        }
        totalCommitCount: defaultBranchRef {
          target {
            ... on Commit {
              history(first: 1) {
                totalCount
                nodes {
                  committedDate
                }
              }
            }
          }
        }
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

repositories_collection = "repositories"

if repositories_collection in mydb.list_collection_names():
  print("The collection exists.")
  repo_conn_collection = mydb[repositories_collection]
else:
  repo_conn_collection = mydb.create_collection(repositories_collection)

def run_query_variables(query, attemp, variables):
  token_1 = "zZx07Qs7B4nzWLvH0waExtyRrOzsNW2Lmp7J"

  token_2 = "GjRyws4PZUKZJJRPvag3lB4I2Wd2hQ2aWvbe"

  if attemp > 5 and attemp <= 10:
    headers = {"Authorization": "Bearer ghp_" + token_2} 
  else:
    headers = {"Authorization": "Bearer ghp_" + token_1}

  request = requests.post(GITHUB_API_ENDPOINT, headers=headers, json={"query": query, "variables": variables})

  if request.status_code == 200:
      return request.json()
  elif attemp <= NUMBER_OF_ATTEMPTS:
      print("Tentativa de conexão falhou :(. {}/{} Tentando novamente...".format(attemp,
            NUMBER_OF_ATTEMPTS))
      sleep(1)
      return run_query_variables(query, attemp + 1, variables)
  else:
      raise Exception("Tentativa de conexão falhou com o erro: {}. {}".format(
          request.status_code, query))

def save_repos(login, repos, today):

  repo_cursor = repo_conn_collection.find({'user': login})
  repo_df = pd.DataFrame(list(repo_cursor))
  if len(repo_df) > 0:
    repos_name = repo_df['repo_name']
  else:
    repos_name = []

  for repo in repos:
    if repo['nameWithOwner'] in list(repos_name):
      print('pula repo')
      continue
    
    if repo['owner']:
        org_name = repo['owner']['name']
        org_member = repo['owner']['membersWithRole']['totalCount']
    else:
        org_name = None
        org_member = None

    created_at = datetime.datetime.strptime(
              repo['createdAt'], '%Y-%m-%dT%H:%M:%SZ')

    accountAgeInDays = today - created_at
    if repo['totalCommitCount']:
        commit_total_count = repo['totalCommitCount']['target']['history']['totalCount']
        last_commit = datetime.datetime.strptime(
                repo['totalCommitCount']['target']['history']['nodes'][0]['committedDate'] , '%Y-%m-%dT%H:%M:%SZ')
    else:
        commit_total_count = None
        last_commit = None

    if repo['primaryLanguage']:
        language = repo['primaryLanguage']['name']
    else:
        language = None

    repository = {
        "user": login,
        "repo_name": repo['nameWithOwner'],
        "created_at": created_at,
        "age_years": accountAgeInDays.total_seconds()/(3600*24*365),
        "stars": repo['stargazerCount'],
        'language': language,
        'total_issues': repo['totalIssues']['totalCount'],
        'closed_issues': repo['closedIssues']['totalCount'],
        'pull_requests': repo['pullRequests']['totalCount'],
        'organization_name': org_name,
        'organization_members': org_member,
        'total_commits': commit_total_count,
        'last_commit':  last_commit
    }
    repo_conn_collection.insert_one(repository)


def fetch_repositories(login):
    today = datetime.datetime.utcnow()
    variables = {"login": login}
    has_next = True
    i = 0
    end_cursor = "null"
    repos = []
    query = INITIAL_QUERY

    response = run_query_variables(query, 1, variables)

    while 'errors' in response:
      response = run_query_variables(query, 1, variables)

    repos += response["data"]["user"]["repositories"]["nodes"]

    has_next = response["data"]["user"]["repositories"]["pageInfo"]["hasNextPage"]

    if has_next:
        end_cursor = response["data"]["user"]["repositories"]["pageInfo"]["endCursor"]

    i += 1

    query = CURSOR_QUERY

    while(has_next):

        variables = {"login": login,"cursor":end_cursor}

        response = run_query_variables(query, 1, variables)

        has_next = response["data"]["user"]["repositories"]["pageInfo"]["hasNextPage"]

        if has_next:
            end_cursor = response["data"]["user"]["repositories"]["pageInfo"]["endCursor"]

        repos += response["data"]["user"]["repositories"]["nodes"]

        print(end_cursor)

        i += 1

    save_repos(login, repos, today)

cursor = user_conn_collection.find({'repositories': {'$gt': 0}})

user_df = pd.DataFrame(list(cursor))

logins = user_df['login'].drop_duplicates()

repo_cursor = repo_conn_collection.find()
repo_df = pd.DataFrame(list(repo_cursor))
if len(repo_df) > 0:
  users = repo_df['user'].drop_duplicates()
  last = users.iloc[-1]
  users.drop(users.index[-1])
else:
  users = []

for login in logins:
    if login in list(users) or login == 'calebccff':
      print('pula usuario')
      continue
    print('usuario: ' + login)
    fetch_repositories(login)

print('Done!')