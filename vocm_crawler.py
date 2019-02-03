import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup

"""
One time script post archived questions of the day from vocm to mongodb
"""

class QOTD:
    def __init__(self):
        self.text = ""
        self.date = ""
        self.responses = []

#%%
query = "http://vocm.com/question-of-the-day-archive/"

try:
    page = requests.get(query)
    soup = BeautifulSoup(page.content, 'html.parser')
except:
    print("error on", query)

#%% Crawl the data

# TODO: update date var to datetime rather than string

qotd_tables = soup.find_all("table", { "class" : "qotd-table" })
qotd_list = []

for qotd_table in qotd_tables:
    qotd = QOTD()
    qotd.text = str(qotd_table).split('<td class="question">')[1].split('</td>')[0]
    qotd.date = str(qotd_table).split('<td class="question-date">')[1].split('</td>')[0]
    
    for row in qotd_table.findAll("tr")[1:]:
        ans = str(row).split('<td>')[1].split('</td>')[0]
        count = str(row).split('<td class="qotd-table-vote">')[1].split('</td>')[0]
        qotd.responses.append((ans, count))
    
    qotd_list.append(qotd)

    
#%% Post to MongoDB

try:
    client = MongoClient('mongodb://admin:admin@cluster0-shard-00-00-xlfzz.gcp.mongodb.net:27017,cluster0-shard-00-01-xlfzz.gcp.mongodb.net:27017,cluster0-shard-00-02-xlfzz.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin')
    db = client['vocm']
    collection = db['qotd']
except:
    print('error connecting to mongo!')
finally:
    client.close()

for qotd in qotd_list:
    collection.insert_one({"text" : qotd.text, 
                           "date" : qotd.date,
                           "responses" : qotd.responses })

