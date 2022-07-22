import os
import pandas as pd
import datetime

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

def dateFromStr(dateStr):
    """Returns a datetime object created from a date string, "yyyy-mm-dd" format

    :param dateStr: String to parse
    :type dateStr: str
    :return: Parsed Date object
    :rtype: datetime.date
    """
    return datetime.date(int(dateStr[:4]), int(dateStr[5:7]), int(dateStr[8:]))

def parseHistorical(fileName, type, startDateTime = datetime.date(1970, 1, 1), endDateTime = datetime.date.today()):
    #todo: Dividends should count if bought before and sold on/after date, splits should count if bought on/before and sold after date
    """Parses a file of historical records, either dividends or splits, into a list of processing instructions

    :param fileName: File to parse
    :type fileName: str
    :param type: Type of instruction
    :type type: str
    :param startDateTime: Date to begin reading, defaults to 1970-01-01
    :type startDateTime: datetime.date, optional
    :param endDateTime: Date to end reading, defaults to current day
    :type endDateTime: datetime.date, optional
    :return: List of instructions
    :rtype: list of dicts with keys {"type", "date", "amount"}
    """
    df = pd.read_json(fileName)
    instructions = []
    if("historical" in df):
        l = list(df['historical'])
        for i in l:
            date = dateFromStr(i["date"])
            if(date>=startDateTime and date<=endDateTime):
                if(type == "split"):
                    instructions.append({"type": "split", "date": i["date"], "amount": i["numerator"]/i["denominator"]})
                elif(type == "dividend"):
                    instructions.append({"type": "dividend", "date": i["date"], "amount": i["dividend"]})
                else:
                    print("Unknown instruction type")
    return instructions

def getSymbolReturn(symbol, endPrice, startDate, endDate):
    """For a given symbol between two dates, sequentially tabulate all dividends and factor for all splits, and return the adjusted return on investment

    :param symbol: Stock symbol
    :type symbol: str
    :param endPrice: Price on endDate
    :type endPrice: float
    :param startDate: Date to begin tabulating
    :type startDate: str, "yyyy-mm-dd"
    :param endDate: Date to end tabulating
    :type endDate: str, "yyyy-mm-dd"
    :return: Total return on investment per share over time period
    :rtype: float
    """
    startDateTime = dateFromStr(startDate)
    endDateTime = dateFromStr(endDate)
    
    dividends = "Stock-Evaluator/API Archives/"+symbol+"_dividends.json"
    splits = "Stock-Evaluator/API Archives/"+symbol+"_splits.json"

    instructions = parseHistorical(splits, "split", startDateTime, endDateTime)
    instructions += parseHistorical(dividends, "dividend", startDateTime, endDateTime)    
    instructions = sorted(instructions, key = lambda i: i['date'])

    shares = 1
    dividends = 0
    for i in instructions:
        if(i["type"] == "split"):
            shares *= i["amount"]
        elif(i["type"] == "dividend"):
            dividends += i["amount"]*shares
        else:
            print("Unknown instruction type")

    return endPrice*shares+dividends

def parseFinancialStatement(symbol, statement, startYear, endYear):
    """Reads financial statement data from a fetched file between two given years

    :param symbol: Stock symbol to parse data for
    :type symbol: str
    :param statement: Financial statement to read features from
    :type statement: str
    :param startYear: First year to include features from
    :type startYear: int
    :param endYear: Last year to include features from
    :type endYear: int
    :return: Single-row DataFrame, containing values of each feature for each year
    :rtype: pandas.DataFrame
    """
    fileName = "Stock-Evaluator/API Archives/"+symbol+"_"+statement+".json"
    df = pd.read_json(fileName)

    dropCols = ["date", "reportedCurrency", "cik", "fillingDate", "acceptedDate", "period", "link", "finalLink"]
    df.drop(labels = dropCols, axis = 1, inplace = True)

    df = df[df["calendarYear"]<=endYear]
    df = df[df["calendarYear"]>=startYear]
    df["calendarYear"] = df["calendarYear"].astype("int64")
    df = df.drop_duplicates('calendarYear')

    df = df.melt(id_vars=["symbol", "calendarYear"])

    df["column"] = "y"+(df["calendarYear"]-endYear).astype(str)+"_"+statement+"_"+df["variable"]
    df.drop(labels = ["calendarYear", "variable"], axis = 1, inplace = True)

    df = pd.pivot(df, index="symbol", columns="column", values="value")

    return df