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

user_docs = user_conn_collection.find({}, {"login":1})
foll_docs = foll_conn_collection.find({})

users = [user["login"] for user in user_docs]
metrics = []

for user in users:
    data = []
    
    comm_followed = [doc for doc in foll_docs if doc['following'] == user and doc['followed'] in users]
    comm_following = [doc for doc in foll_docs if doc['followed'] == user and doc['following'] in users]
    metric = {
        "login": user,
        "comm_followed": len(comm_followed),
        "comm_following": len(comm_following)
    }

    metrics.append(metric)

metrics_conn_collection.insert_many(metrics)

