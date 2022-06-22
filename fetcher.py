import urllib3
import utils
import os

def fetchStatement(url, fileName, http):
    r = http.request('GET', url)
    target = open(fileName, "w")

    target.write(r.data.decode('utf8'))
    target.close()

def fetchStatements(symbols, queries, overwrite=False):
    apikey = open("apikey.txt", "r").read()
    http = urllib3.PoolManager()
    filesWritten = 0

    for symbol in symbols:
        for query in queries:
            endpoint = query["endpoint"]
            params = query["params"]
            name = query["name"]

            url = "https://financialmodelingprep.com/api/v3/"+endpoint+"/"+symbol+"?"+params+"&apikey="+apikey

            fileName = "API Archives/"+symbol+"_"+name+".json"
            
            if(overwrite or not os.path.exists(fileName)):
                fetchStatement(url, fileName, http)
                filesWritten+=1
    
    return filesWritten


symbols = utils.readSymbols("symbols.txt")
labelDate = "2022-01-03"
futureDate = "2022-06-01"

queries = [
    {"endpoint":"income-statement", "params":"limit=120", "name":"income_statement"},
    {"endpoint":"balance-sheet-statement", "params":"limit=120", "name":"balance_sheet"},
    {"endpoint":"cash-flow-statement", "params":"limit=120", "name":"cash_flow"},
    {"endpoint":"historical-price-full", "params":"from="+labelDate+"&to="+labelDate, "name":"price_label"},
    {"endpoint":"historical-price-full", "params":"from="+futureDate+"&to="+futureDate, "name":"price_future"},
    #{"endpoint":"historical-market-capitalization", "params":"limit=120", "name":"market_cap"}
    ]

input("Input any text to attempt "+str(len(symbols)*len(queries))+" API requests")

result = fetchStatements(symbols = symbols, queries = queries)

print("Successfully wrote "+str(result)+" files")