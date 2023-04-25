import pymongo
import matplotlib.pyplot as plt
import re

connection_string = f"mongodb+srv://pvfcosta:dsh2023.retorno@ti6-lbtqia-research.bdfqdy0.mongodb.net/test"

client = pymongo.MongoClient(connection_string)

mydb = client['ti-data']

user_collection = "users"
user_conn_collection = mydb[user_collection]

pipeline = [
    { "$group": { "_id": "$location", "count": { "$sum": 1 } } },
    { "$sort": { "count": -1 } }
]

result = list(user_conn_collection.aggregate(pipeline))

x1 = int(re.findall(r'\d+', str(result[1]))[0])
x2 = int(re.findall(r'\d+', str(result[2]))[0])
x3 = int(re.findall(r'\d+', str(result[3]))[0])
x4 = int(re.findall(r'\d+', str(result[4]))[0])
x5 = int(re.findall(r'\d+', str(result[5]))[0])

columns = ('Germany', 'United States', 'Seattle, WA', 'USA', 'Brazil')
values = [x1, x2, x3, x4, x5]

query = {"location": {"$nin": [columns]}}

x6 = user_conn_collection.count_documents(query)

print(x6)

plt.bar(columns, values)

plt.xlabel('Regiões')
plt.ylabel('Número de ocorrência')
plt.title('Usuários da comunidade por região')

plt.show()
