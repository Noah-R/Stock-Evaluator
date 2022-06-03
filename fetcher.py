import urllib3

symbols = open("stock_symbols.txt", "r")
apikey = open("apikey.txt", "r").read()

for line in symbols:
    symbol = str(line).strip().upper()
    
    for statement in ["income-statement", "balance-sheet", "cash-flow"]:
        url = "https://financialmodelingprep.com/api/v3/"+statement+"/"+symbol+"?limit=120&apikey="+apikey

        http = urllib3.PoolManager()
        r = http.request('GET', url)

        target = open("API Archives/"+symbol+"-"+statement+".json", "w")
        target.write(r.data.decode('utf8'))
        target.close()