import requests
import pandas as pd
import matplotlib.pyplot as plot
import pymongo

connection_string = f"mongodb+srv://pvfcosta:dsh2023.retorno@ti6-lbtqia-research.bdfqdy0.mongodb.net/test"

client = pymongo.MongoClient(connection_string)

mydb = client['ti-data']

user_collection = "users"

if user_collection in mydb.list_collection_names():
  user_conn_collection = mydb[user_collection]
else:
    print("The collection doesn't exist.")

follow_collection = "follow"

if follow_collection in mydb.list_collection_names():
  foll_conn_collection = mydb[follow_collection]
else:
    print("The collection doesn't exist.")

metrics_collection = "follow_metrics"

if metrics_collection in mydb.list_collection_names():
  print("The collection exists.")
  metrics_conn_collection = mydb[metrics_collection]
else:
  metrics_conn_collection = mydb.create_collection(metrics_collection)

user_docs = user_conn_collection.find({},{"login":1})
foll_docs = foll_conn_collection.find()

df_foll = pd.DataFrame(list(foll_docs))

users = pd.DataFrame(list(user_docs))
metrics = []
logins = users['login'].tolist();

for login in logins:
    mask_followed = ((df_foll['following'] == login) & df_foll['followed'].isin(logins))
    mask_following = ((df_foll['followed'] == login) & df_foll['following'].isin(logins))
    comm_followed = df_foll[mask_followed]
    comm_following = df_foll[mask_following]
    metric = {
        "login": login,
        "comm_followed": len(comm_followed),
        "comm_following": len(comm_following)
    }

    metrics.append(metric)

metrics_conn_collection.insert_many(metrics)

