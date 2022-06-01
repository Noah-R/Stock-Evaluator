import urllib3

f = open("dow_symbols.txt", "r")
apikey = open("apikey.txt", "r").read()

for line in f:
    symbol = str(line).strip().upper()

    url = "https://financialmodelingprep.com/api/v3/income-statement/"+symbol+"?limit=120&apikey="+apikey#income becomes balance-sheet or cash-flow

    http = urllib3.PoolManager()
    r = http.request('GET', url)

    target = open("API Archives/"+symbol+"_income.json", "w")
    target.write(r.data.decode('utf8'))
    target.close()