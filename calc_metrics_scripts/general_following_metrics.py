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

if user_collection in mydb.list_collection_names():
  user_conn_collection = mydb[user_collection]
else:
    print("The collection doesn't exist.")

cursor = user_conn_collection.find({})

follow =  [{'followers': int(doc["followers"]), 'following': int(doc["following"]) } for doc in cursor]

lista_followers = [obj['followers'] for obj in follow]
lista_following = [obj['following'] for obj in follow]

df_followers = pd.DataFrame({'followers': lista_followers})
df_following = pd.DataFrame({'following': lista_following})

sns.boxplot(x=df_followers['followers'])
plot.title("Número de followers")
plot.savefig("followers.png")

plot.clf()

sns.boxplot(x=df_following['following'])
plot.title("Número de following")
plot.savefig("following.png")