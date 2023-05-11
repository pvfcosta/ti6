import requests
import pandas as pd
import matplotlib.pyplot as plot
import pymongo
import pandas as pd
import seaborn as sns

connection_string = f"mongodb+srv://pvfcosta:dsh2023.retorno@ti6-lbtqia-research.bdfqdy0.mongodb.net/test"

client = pymongo.MongoClient(connection_string)

mydb = client['ti-data']

user_collection = "users"

follow_metrics_collection = "follow_metrics"

if user_collection in mydb.list_collection_names():
  user_conn_collection = mydb[user_collection]
else:
    print("The collection doesn't exist.")

cursor = user_conn_collection.find()

df = pd.DataFrame(list(cursor))

a4_dims = (10, 14)
fig, ax = plot.subplots(figsize=a4_dims)
chart = sns.histplot(ax=ax, x=df['search'])
chart.tick_params(axis='x', rotation=90)
plot.title("Número de usuários x Palavra-chave")
plot.savefig("keyword.png")

plot.clf()

a4_dims = (7, 7)
fig, ax = plot.subplots(figsize=a4_dims)
sns.histplot(ax=ax, x=df['accountAge'])
plot.title("Número de usuários x Idade da Conta")
plot.savefig("age.png")

plot.clf()
