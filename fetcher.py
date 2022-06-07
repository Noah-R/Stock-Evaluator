import urllib3

def fetchStatements(symbols, queries):
    apikey = open("apikey.txt", "r").read()
    http = urllib3.PoolManager()
    filesWritten = 0

    for symbol in symbols:
        for query in queries:
            url = "https://financialmodelingprep.com/api/v3/"+query["endpoint"]+"/"+symbol+"?"+query["params"]+"&apikey="+apikey
            
            r = http.request('GET', url)

            target = open("API Archives/"+symbol+"-"+query["endpoint"]+".json", "w")
            target.write(r.data.decode('utf8'))
            target.close()
            filesWritten+=1
    
    return filesWritten


symbolList = open("stock_symbols.txt", "r")
symbols = []
for line in symbolList:
        symbols.append(str(line).strip().upper())

queries = [
    {"endpoint":"income-statement", "params":"limit=120"},
    {"endpoint":"balance-sheet", "params":"limit=120"},
    {"endpoint":"cash-flow", "params":"limit=120"},
    {"endpoint":"historical-price-full", "params":"from=2022-01-03&to=2022-01-03"},
    {"endpoint":"market-captialization", "params":"limit=120"}
    ]

result = fetchStatements(symbols = symbols, queries = queries)
print("Successfully wrote "+str(result)+" files")