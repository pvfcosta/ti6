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

if follow_metrics_collection in mydb.list_collection_names():
  follow_metrics_conn_collection = mydb[follow_metrics_collection]
else:
    print("The collection doesn't exist.")

cursor = user_conn_collection.find()

follow_cursor = follow_metrics_conn_collection.find()

df = pd.DataFrame(list(cursor))

df_follow = pd.DataFrame(list(follow_cursor))

follow =  df[['followers', 'following']]

sns.boxplot(x=df['followers'])
plot.title("Número de followers")
plot.savefig("followers.png")

plot.clf()

sns.boxplot(x=df['following'])
plot.title("Número de following")
plot.savefig("following.png")

plot.clf()

sns.boxplot(data=df_follow[['comm_followed','comm_following']], orient='v')
plot.title("Número de Seguidores e Seguides em Comum")
plot.savefig("common_following.png")