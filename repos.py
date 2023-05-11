
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
token = "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"

CURSOR_QUERY = """
query($login:String!,$cursor:String!)
{
  user(login: $login) {
    repositories(first: 50, after:$cursor) {
      nodes {
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
    repositories(first: 10, after:null) {
      nodes {
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

        headers = {"Authorization": "Bearer " + token}

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
    for repo in repos:
        print(repo)
        
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

cursor = user_conn_collection.find({})    

for document in cursor:
    login = document['login']
    print('usuario: ' + login)
    fetch_repositories(login)

print('Done!')