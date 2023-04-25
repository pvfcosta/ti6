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

sponsor_collection = "sponsor"

if sponsor_collection in mydb.list_collection_names():
    spon_conn_collection = mydb[sponsor_collection]
else:
    print("The collection doesn't exist.")

metrics_collection = "sponsor_metrics"

if metrics_collection in mydb.list_collection_names():
    print("The collection exists.")
    metrics_conn_collection = mydb[metrics_collection]
else:
    metrics_conn_collection = mydb.create_collection(metrics_collection)

user_docs = user_conn_collection.find({}, {"login": 1})
spon_docs = spon_conn_collection.find({})

users = [user["login"] for user in user_docs]
metrics = []

for user in users:
    data = []

    comm_sponsors = [doc for doc in spon_docs if doc['sponsoring'] == user and doc['sponsors'] in users]
    comm_sponsoring = [doc for doc in spon_docs if doc['sponsors'] == user and doc['sponsoring'] in users]
    metric = {
        "login": user,
        "comm_sponsors": len(comm_sponsors),
        "comm_sponsoring": len(comm_sponsoring)
    }

    metrics.append(metric)

metrics_conn_collection.insert_many(metrics)

