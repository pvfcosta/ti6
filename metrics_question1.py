
import pandas as pd
import pymongo
import matplotlib.pyplot as plot

connection_string = f"mongodb+srv://pvfcosta:dsh2023.retorno@ti6-lbtqia-research.bdfqdy0.mongodb.net/test"

client = pymongo.MongoClient(connection_string)

mydb = client['ti-data']

user_collection = "users"
user_conn_collection = mydb[user_collection]

users = pd.DataFrame(user_conn_collection.find({}))

# idade da conta
accountAge = users.hist(column='accountAge', grid=False)

plot.title('Idade da conta em dias x Quantidade de usuários')
plot.savefig('graficos/accountAge.png')
plot.clf()
# frequencia de commits
# commitsPerWeek = users.boxplot(column='commitsPerWeek')

# plot.title('Commits por semana x Quantidade de usuários')
# commitsPerWeek.plot()
# plot.savefig('graficos/commitsPerWeek_boxplot.png')

commitsPerWeekH = users.hist(column='commitsPerWeek', grid=False)
plot.title('Commits por semana x Quantidade de usuários')
plot.savefig('graficos/commitsPerWeek_hist.png')
plot.clf()

users['commitsPerWeek1'] = users['commitsPerWeek'] + 1
commitsPerWeekH = users.hist(column='commitsPerWeek1', grid=False)
plot.yscale('log')
plot.title('Commits por semana x Quantidade de usuários')
plot.savefig('graficos/commitsPerWeek_hist_log.png')
plot.clf()
# cpw = pd.Series(users['commitsPerWeek'])

# densityplot = cpw.plot.kde()
# plot.title('Commits por semana x Quantidade de usuários')
# plot.savefig('graficos/commitsPerWeek_dens.png')

# issues
# issues = users.boxplot(column='issues')

# plot.title('Quantidades de Issues x Quantidade de usuários')
# issues.plot()
# plot.savefig('graficos/issues_b.png')

issuesH = users.hist(column='issues', grid=False)

plot.title('Quantidades de Issues x Quantidade de usuários')
plot.savefig('graficos/issues_hist.png')
plot.clf()

users['issues1'] = users['issues'] + 1
issuesH = users.hist(column='issues1', grid=False)
plot.yscale('log')
plot.title('Quantidades de Issues x Quantidade de usuários')
plot.savefig('graficos/issues_hist_log.png')
plot.clf()

# pull requests
prs = users.hist(column='pullRequests', grid=False)

plot.title('Quantidades de Pull Requests x Quantidade de usuários')
plot.savefig('graficos/prs.png')
plot.clf()

users['pullRequests1'] = users['pullRequests'] + 1
prs = users.hist(column='pullRequests', grid=False)
plot.yscale('log')
plot.title('Quantidades de Pull Requests x Quantidade de usuários')
plot.savefig('graficos/prs_log.png')
plot.clf()
# ax = users.plot(x="Quantidade de usuários", y=['issues', 'pullRequests'], kind='bar', rot=0, stacked=True)
# plot.title('Quantidades de Pull Requests e Issues x Quantidade de usuários')
# plot.savefig('graficos/issues_prs.png')
# plot.clf()