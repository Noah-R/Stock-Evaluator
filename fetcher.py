import urllib3

def fetchStatements(symbols, endpoints, params):
    apikey = open("apikey.txt", "r").read()
    http = urllib3.PoolManager()
    filesWritten = 0

    for symbol in symbols:        
        for statement in endpoints:
            url = "https://financialmodelingprep.com/api/v3/"+statement+"/"+symbol+"?"+params+"&apikey="+apikey

            r = http.request('GET', url)

            target = open("API Archives/"+symbol+"-"+statement+".json", "w")
            target.write(r.data.decode('utf8'))
            target.close()
            filesWritten+=1
    
    return filesWritten


symbolList = open("stock_symbols.txt", "r")
symbols = []
for line in symbolList:
        symbols.append(str(line).strip().upper())
symbols=symbols[1:]

#todo: combine endpoint and param into a single struct
endpoints = []#["income-statement", "balance-sheet", "cash-flow", "historical-price-full", "market-capitalization"]

params = "limit=120"#historical-price-full has params "from=2022-01-03&to=2022-01-03" instead

result = fetchStatements(symbols = symbols, endpoints = endpoints, params = params)
print("Successfully wrote "+str(result)+" files")