import urllib3
import os

def fetchFile(url, fileName, http):
    """Handles a single request to the FinancialModelingPrep API

    :param url: Endpoint URL to request
    :type url: str
    :param fileName: Relative path of filename to write response data to
    :type fileName: str
    :param http: urllib3 Pool Manager object
    :type http: urllib3.PoolManager
    """
    r = http.request('GET', url)
    target = open(fileName, "w")

    target.write(r.data.decode('utf8'))
    target.close()

def fetchEndpoints(symbols, queries, overwrite=False):
    """Fetches financial data from a series of endpoints for a series of stock symbols

    :param symbols: List of stock symbols to fetch data for
    :type symbols: list
    :param queries: List of queries to perform for each symbol 
    :type queries: list of dictionaries with keys {endpoint, params, name}
    :param overwrite: Whether to overwrite existing files if present, defaults to False
    :type overwrite: bool, optional
    :return: Number of new files written
    :rtype: int
    """
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