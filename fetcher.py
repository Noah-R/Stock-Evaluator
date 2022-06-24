import urllib3
import utils
import os
import json

def fetchFile(url, fileName, http):
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
                fetchFile(url, fileName, http)
                filesWritten+=1
    
    return filesWritten

def fetchBenchmarks(dates, symbol = "VTSAX", overwrite=False):#S&P 500 symbol: %5EGSPC
    apikey = open("apikey.txt", "r").read()
    http = urllib3.PoolManager()
    filesWritten = 0
    names = ["labelDate", "futureDate"]

    for i in range(len(dates)):
        url = "https://financialmodelingprep.com/api/v3/historical-price-full/"+symbol+"?from="+dates[i]+"&to="+dates[i]+"&apikey="+apikey

        fileName = "API Archives/benchmark_"+names[i]+".json"

        if(overwrite or not os.path.exists(fileName)):
            fetchFile(url, fileName, http)
            filesWritten+=1
    
    return filesWritten

def writeDates(labelDate, futureDate):
    #deprecated, for use fetching market return on the fly
    dates = {"labelDate": labelDate, "futureDate": futureDate}
    f = open("dates.txt", "w")
    json.dump(dates, f)
    f.close()

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

input("Input any text to attempt "+str(len(symbols)*len(queries)+2)+" API requests")

result = fetchStatements(symbols = symbols, queries = queries)
result += fetchBenchmarks([labelDate, futureDate])

print("Successfully wrote "+str(result)+" files")