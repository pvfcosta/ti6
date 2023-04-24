
import requests
import pandas as pd
import datetime

# colocar token aqui
token = "VzC9sNghkF0NWRtRC2e5oMzbH6dIQI2sHsP4"

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
    wordResults = {
        'search': [],
        'login': [],
        'name': [],
        'bio': [],
        'bioHTML': [],
        'url': [],
        'pronouns': [],
        'createdAt': [],
        'location': [],
        'status': [],
        'pullRequests': [],
        'issues': [],
        'organizations': [],
        'totalCommitContributions': [],
        'commitsStartedAt': [],
        'commitsEndedAt': [],
        'commitsPerWeek': [],
        'accountAge': [],
        'followers': [],
        'following': [],
        'sponsors': [],
        'sponsoring': []
    }
    while True:
        request = requests.post('https://api.github.com/graphql',
                                json={'query': query}, headers=headers)
        result = request.json()
        if 'data' in result and result['data'] is not None:
            allResults += result['data']['search']['nodes']

            # logica pra separar por aba da tabela
            for node in result['data']['search']['nodes']:
                wordResults['search'].append(word)
                wordResults['login'].append(node['login'])
                wordResults['name'].append(node['name'])
                wordResults['url'].append(node['url'])
                wordResults['bio'].append(node['bio'])
                wordResults['bioHTML'].append(node['bioHTML'])
                wordResults['pronouns'].append(node['pronouns'])
                wordResults['createdAt'].append(node['createdAt'])
                wordResults['location'].append(node['location'])
                wordResults['status'].append(node['status'])
                wordResults['pullRequests'].append(node['pullRequests']['totalCount'])
                wordResults['issues'].append(node['issues']['totalCount'])
                wordResults['organizations'].append(
                    node['organizations']['totalCount'])
                wordResults['totalCommitContributions'].append(
                    node['contributionsCollection']['totalCommitContributions'])
                wordResults['commitsStartedAt'].append(
                    node['contributionsCollection']['startedAt'])
                wordResults['commitsEndedAt'].append(
                    node['contributionsCollection']['endedAt'])
                createdAt = datetime.datetime.strptime(
                    node['createdAt'], '%Y-%m-%dT%H:%M:%SZ')
                accountAgeInDays = today - createdAt
                wordResults['accountAge'].append(accountAgeInDays.days)
                wordResults['followers'].append(node['followers']['totalCount'])
                wordResults['following'].append(node['following']['totalCount'])
                wordResults['sponsors'].append(node['sponsors']['totalCount'])
                wordResults['sponsoring'].append(node['sponsoring']['totalCount'])

                # calcula frequencia de commits
                commitsStartedAt = datetime.datetime.strptime(
                    node['contributionsCollection']['startedAt'], '%Y-%m-%dT%H:%M:%SZ')
                commitsEndedAt = datetime.datetime.strptime(
                    node['contributionsCollection']['endedAt'], '%Y-%m-%dT%H:%M:%SZ')
                contributionTime = commitsEndedAt - commitsStartedAt
                commitsPerWeek = node['contributionsCollection']['totalCommitContributions'] / ( contributionTime.days / 7 )
                wordResults['commitsPerWeek'].append(commitsPerWeek)
               
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
    allWordsResults.append(wordResults)

members = pd.Series(membersColumn, name='members')

dfOrgs = pd.DataFrame(allOrganizations)

dfOrgs.to_csv('organizations.csv', index=False, sep=';', encoding='utf-8')

df = pd.read_csv('organizations.csv', sep=";")
teste_concat = pd.concat([df, members], axis=1)
teste_concat.to_csv('organizations.csv', index=False, sep=';', encoding='utf-8')

with pd.ExcelWriter('users.xlsx', engine='xlsxwriter') as writer:
    for wordResults in allWordsResults:
        dfWord = pd.DataFrame(wordResults)
        if len(wordResults['search']) > 0:
          dfWord.to_excel(
              writer, sheet_name=wordResults['search'][0], index=False)

