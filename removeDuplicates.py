import pandas as pd
import pymongo

connection_string = f"mongodb+srv://pvfcosta:dsh2023.retorno@ti6-lbtqia-research.bdfqdy0.mongodb.net/test"

client = pymongo.MongoClient(connection_string)

mydb = client['ti-data']

user_no_dup_collection = "users_no_duplicates"
user_collection = "users"

user_conn_collection = mydb[user_collection]

if user_no_dup_collection in mydb.list_collection_names():
    print("The users no duplication collection exists.")
    user_no_dup_conn_collection = mydb[user_no_dup_collection]
else:
    user_no_dup_conn_collection = mydb.create_collection(user_no_dup_collection)

users = list(user_conn_collection.find({}))
users = pd.DataFrame(users).drop_duplicates(subset=['login'])

user_no_dup_conn_collection.delete_many({})
user_no_dup_conn_collection.insert_many(users.to_dict('records'))
