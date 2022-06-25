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

    for date in dates:
        url = "https://financialmodelingprep.com/api/v3/historical-price-full/"+symbol+"?from="+date+"&to="+date+"&apikey="+apikey

        fileName = "API Archives/benchmark_price_"+date+".json"

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
dates = ["2022-01-03", "2022-06-01"]

queries = [
    {"endpoint":"income-statement", "params":"limit=120", "name":"income_statement"},
    {"endpoint":"balance-sheet-statement", "params":"limit=120", "name":"balance_sheet"},
    {"endpoint":"cash-flow-statement", "params":"limit=120", "name":"cash_flow"}
    ]
for date in dates:
    queries.append({"endpoint":"historical-price-full", "params":"from="+date+"&to="+date, "name":"price_"+date})

input("Input any text to attempt "+str(len(symbols)*len(queries)+len(dates))+" API requests")

result = fetchStatements(symbols = symbols, queries = queries)
result += fetchBenchmarks(dates)

print("Successfully wrote "+str(result)+" files")