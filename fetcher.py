import urllib3
import utils
import os

def fetchStatements(symbols, queries, overwrite=False):
    apikey = open("apikey.txt", "r").read()
    http = urllib3.PoolManager()
    filesWritten = 0

    for symbol in symbols:
        for query in queries:
            endpoint = query["endpoint"]
            params = query["params"]

            url = "https://financialmodelingprep.com/api/v3/"+endpoint+"/"+symbol+"?"+params+"&apikey="+apikey

            fileName = "API Archives/"+symbol+"-"+endpoint+".json"
            
            if(overwrite or not os.path.exists(fileName)):
                r = http.request('GET', url)
                target = open(fileName, "w")

                target.write(r.data.decode('utf8'))
                target.close()

                filesWritten+=1
    
    return filesWritten


symbols = utils.readSymbols("symbols.txt")

queries = [
    {"endpoint":"income-statement", "params":"limit=120"},
    {"endpoint":"balance-sheet-statement", "params":"limit=120"},
    {"endpoint":"cash-flow-statement", "params":"limit=120"},
    #{"endpoint":"historical-price-full", "params":"from=2022-01-03&to=2022-01-03"},
    {"endpoint":"historical-market-capitalization", "params":"limit=120"}
    ]

result = fetchStatements(symbols = symbols, queries = queries)

print("Successfully wrote "+str(result)+" files")