
import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plot
import json

# colocar token aqui
token = "9OB8VQzEgURy2ztZBs0T4qNZxO9UTi3kLLDr"

headers = {"Authorization": "bearer ghp_"+token}

allResults = []

query = """
{
  search(type: USER, first: 30, query: "queer in:bio") {
    userCount
    pageInfo {
      endCursor
      startCursor
    }
    edges {
      node {
        ... on User {
          name
          login
          bio
        }
      }
    }
  }
}
"""

endCursor = "null"

error = 0
while (len(allResults) < 1000):
    request = requests.post('https://api.github.com/graphql',
                            json={'query': query}, headers=headers)
    result = request.json()
    if 'data' in result:
      nodes = result['data']['search']['edges']
      for node in nodes:
        if node['node'] and node['node']['bio']:
          allResults.append(node['node'])

      query = query.replace(endCursor, '"'+result['data']
                              ['search']['pageInfo']['endCursor']+'"')
      endCursor = '"'+result['data']['search']['pageInfo']['endCursor']+'"'
    else:
        error += 1
        if (error > 5):
            print("Error na chamada da api do git hub")
            print(result)
            break
        else:
            continue

# today = datetime.datetime.utcnow()

# def age(createdAt):
#   age = today.year - createdAt.year - ((today.month, today.day) < (createdAt.month, createdAt.day))
#   return age

# def ageInMonths(createdAt):
#   time = today - createdAt
#   months = 0
#   days = 0
#   seconds = 0
#   microseconds = 0

#   if time.days > 0:
#     days = time.days/30
#   if time.seconds > 0:
#     seconds = time.seconds/(3600*30)
#   if time.microseconds > 0:
#     microseconds = time.microseconds/(3600000*30)

#   print(time.days)
#   print(days)
#   print(time.seconds)
#   print(seconds)
#   print(time.microseconds)
#   print(microseconds)

#   months = days + seconds + microseconds

#   print(months)

#   return float(months)

# def differenceInDays(updatedAt):
#   time = today - updatedAt
#   result = 0
#   days = 0
#   seconds = 0
#   microseconds = 0

#   if time.days > 0:
#     days = time.days
#   if time.seconds > 0:
#     seconds = time.seconds/3600
#   if time.microseconds > 0:
#     microseconds = time.microseconds/3600000

#   result = days + seconds + microseconds

#   return result

# for result in allResults:
#     result['pullRequests'] = result['pullRequests']['totalCount']
#     releases = result['releases']['totalCount']
#     result['releases'] = releases
#     if result['primaryLanguage'] is not None:
#         result['primaryLanguage'] = result['primaryLanguage']['name']
#     result['issues'] = result['issues']['totalCount']
#     closedIssues = result['closedIssues']['totalCount']
#     result['closedIssues'] = closedIssues
#     createdAt = datetime.datetime.strptime(
#         result['createdAt'], '%Y-%m-%dT%H:%M:%SZ')
#     result['createdAt'] = datetime.datetime.strftime(
#         createdAt, '%d/%m/%Y %H:%M:%S')
#     updatedAt = datetime.datetime.strptime(
#         result['updatedAt'], '%Y-%m-%dT%H:%M:%SZ')
#     result['updatedAt'] = datetime.datetime.strftime(
#         updatedAt, '%d/%m/%Y %H:%M:%S')
#     result['ageInYears'] = age(createdAt)
#     months = ageInMonths(createdAt)
#     result['ageInMonths'] = months
#     if months > 0:
#       result['releasesMonth'] = releases/months
#     result['daysFromUpdate'] = differenceInDays(updatedAt)


df = pd.DataFrame(allResults)

df.to_csv('dados.csv', index=False, sep=';',encoding='utf-8')

# ageHist = df.hist(column='ageInYears',bins=7)

# plot.title('Quantidade de Repositórios x Idade (anos)')

# plot.savefig('graficos/ageHist.png')

# pullRequestHist = df.hist(column='pullRequests',bins=6)

# plot.title('Quantidade de Repositórios x Número de Pull Requests')

# plot.savefig('graficos/prHist.png')

# releasesHist = df.hist(column='releasesMonth',bins=4)

# plot.title('Quantidade de Repositórios x Média de Releases por Mês')

# plot.savefig('graficos/releaseHist.png')