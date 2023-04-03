
import requests
import pandas as pd
import matplotlib.pyplot as plot

# colocar token aqui
token = "9OB8VQzEgURy2ztZBs0T4qNZxO9UTi3kLLDr"

headers = {"Authorization": "bearer ghp_"+token}

allResults = []
allWordsResults = []

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
        organizations(first: 10) {
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
        'status': [],
        'organizations': []
    }
    while True:
        request = requests.post('https://api.github.com/graphql',
                                json={'query': query}, headers=headers)
        result = request.json()
        if 'data' in result:
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
                wordResults['status'].append(node['status'])
                wordResults['organizations'].append(
                    node['organizations']['totalCount'])

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

with pd.ExcelWriter('users.xlsx', engine='xlsxwriter') as writer:
    for wordResults in allWordsResults:
        dfWord = pd.DataFrame(wordResults)
        dfWord.to_excel(
            writer, sheet_name=wordResults['search'][0], index=False)