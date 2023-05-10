import requests
import pandas as pd
import matplotlib.pyplot as plot
import pymongo
import seaborn as sns

connection_string = f"mongodb+srv://pvfcosta:dsh2023.retorno@ti6-lbtqia-research.bdfqdy0.mongodb.net/test"

client = pymongo.MongoClient(connection_string)

mydb = client['ti-data']

repositories_collection = "repositories"

if repositories_collection in mydb.list_collection_names():
  repositories_conn_collection = mydb[repositories_collection]
else:
    print("The collection doesn't exist.")

repo_docs = repositories_conn_collection.find()

df_repo = pd.DataFrame(list(repo_docs))

sns.boxplot(x=df_repo['stargazers'])
plot.title("Número de estrelas")
plot.savefig("stargazers.png")

plot.clf()

sns.histplot(x=df_repo['primaryLanguage'])
plot.title("Linguagagem Principal")
plot.savefig("language.png")

plot.clf()




