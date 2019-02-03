import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

class QOTD:
    def __init__(self):
        self.text = ""
        self.date = ""
        self.responses = []


def x_days_ago_qotd(x):
    query = "http://vocm.com/question-of-the-day-archive/"
    
    try:
        page = requests.get(query)
        soup = BeautifulSoup(page.content, 'html.parser')
    except:
        print("error on", query)
    
    
    qotd_table = soup.find_all("table", { "class" : "qotd-table" })
    
    qotd = QOTD()
    qotd.text = str(qotd_table[x]).split('<td class="question">')[1].split('</td>')[0]
    qotd.date = str(qotd_table[x]).split('<td class="question-date">')[1].split('</td>')[0]
    
    for row in qotd_table[x].findAll("tr")[1:]:
        ans = str(row).split('<td>')[1].split('</td>')[0]
        count = str(row).split('<td class="qotd-table-vote">')[1].split('</td>')[0]
        qotd.responses.append((ans, count))

    return qotd

def date_qotd(date):
    try:
        client = MongoClient('mongodb://admin:admin@cluster0-shard-00-00-xlfzz.gcp.mongodb.net:27017,cluster0-shard-00-01-xlfzz.gcp.mongodb.net:27017,cluster0-shard-00-02-xlfzz.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin')
        db = client['vocm']
        collection = db['qotd']
    except:
        print('error connecting to mongo!')
    finally:
        client.close()

    qotd = collection.find_one({"date" : date})

    return qotd

def format_qotd(qotd):
    # fix formatting from db
    if type(qotd) is dict:
        temp = qotd
        qotd = QOTD()
        qotd.date = temp['date']
        qotd.text = temp['text']
        qotd.responses = temp['responses']
    
    # find total votes
    total = 0
    for ans, count in qotd.responses:
        if ans != "Total Votes":
            total += int(count)
    
    # format
    responses = qotd.text
    for ans, count in qotd.responses:
        responses += "\n" + ans +  ": " + count
        if ans != "Total Votes":
            a = (int(count)/total)*100
            responses += " (" + "{0:.0f}".format(a) + "%)"

    
    return responses

        
# print(format_qotd(date_qotd("January 2, 2019")))