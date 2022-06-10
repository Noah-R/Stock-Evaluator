import urllib3
import utils

def fetchStatements(symbols, queries):
    apikey = open("apikey.txt", "r").read()
    http = urllib3.PoolManager()
    filesWritten = 0

    for symbol in symbols:
        for query in queries:
            endpoint = query["endpoint"]
            params = query["params"]

            url = "https://financialmodelingprep.com/api/v3/"+endpoint+"/"+symbol+"?"+params+"&apikey="+apikey
            
            r = http.request('GET', url)

            target = open("API Archives/"+symbol+"-"+endpoint+".json", "w")
            target.write(r.data.decode('utf8'))
            target.close()
            
            filesWritten+=1
    
    return filesWritten


symbols = utils.readSymbols("symbols.txt")

queries = [
    {"endpoint":"income-statement", "params":"limit=120"},
    {"endpoint":"balance-sheet", "params":"limit=120"},
    {"endpoint":"cash-flow", "params":"limit=120"},
    #{"endpoint":"historical-price-full", "params":"from=2022-01-03&to=2022-01-03"},
    {"endpoint":"market-captialization", "params":"limit=120"}
    ]

result = fetchStatements(symbols = symbols, queries = queries)
print("Successfully wrote "+str(result)+" files")