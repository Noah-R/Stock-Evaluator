import os
import pandas as pd

def readSymbols(filename, cleanup = True):
    """Parses a text file of line-separated stock symbols into a list

    :param filename: Relative path of file
    :type filename: str
    :param cleanup: Whether or not to alphabetize and remove duplicates from text file, defaults to True
    :type cleanup: bool, optional
    :return: List of stock symbols
    :rtype: list
    """
    symbolList = open(filename, "r")
    symbols = []
    for line in symbolList:
        symbol = str(line).strip().upper()
        if(symbol not in symbols):
            symbols.append(symbol)

    if(cleanup):
        symbols.sort()
        with open(filename, "w") as file:
            for symbol in symbols[:-1]:
                file.write(symbol+"\n")
            file.write(symbols[-1])

    return symbols

def getFileNames(folder):
    """Returns a list of every file name in a given folder

    :param folder: Relative path of folder to search
    :type folder: str
    :return: List of file names
    :rtype: list
    """
    fileNames = []
    for file in os.listdir(folder):
        filename = os.fsdecode(file)
        fileNames.append(folder+"/"+filename)
    return fileNames

def writeSymbols(symbols, target):
    """Writes a list of stock symbols to a line-separated text file

    :param symbols: List of stock symbols
    :type symbols: list
    :param target: Relative path of file to write to
    :type target: str
    """
    f = open(target, "w")
    for symbol in symbols:
        f.write(symbol+"\n")
    f.close()

def parsePrice(symbol, date):
    """Reads stock price data from a fetched file

    :param symbol: Stock symbol to find price for
    :type symbol: str
    :param date: Date to find stock price on
    :type date: str, "yyyy-mm-dd"
    :return: Stock price of symbol on date, None if unavailable
    :rtype: int
    """
    fileName = "Stock-Evaluator/API Archives/"+symbol+"_price_"+date+".json"
    df = pd.read_json(fileName)

    if("historical" in df):
        return df["historical"].apply(lambda x: round(x["close"], 2))[0]

    return None