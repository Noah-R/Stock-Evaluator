import pandas as pd
import utils
import os

def parseFinancialStatement(symbol, statement, startYear, endYear):
    fileName = "API Archives/"+symbol+"_"+statement+".json"
    df = pd.read_json(fileName)

    dropCols = ["date", "reportedCurrency", "cik", "fillingDate", "acceptedDate", "period", "link", "finalLink"]
    df.drop(labels = dropCols, axis = 1, inplace = True)

    df = df[df["calendarYear"]<=endYear]
    df = df[df["calendarYear"]>=startYear]
    df["calendarYear"] = df["calendarYear"].astype("int64")
    df = df.drop_duplicates('calendarYear')

    #placeholder code for identifying symbols with missing data
    #for year in range(startYear, endYear+1):
    #    if(year not in set(df["calendarYear"])):
    #        print(df["symbol"].iloc[0]+" is missing "+statement+" data from "+str(year))

    df = df.melt(id_vars=["symbol", "calendarYear"])

    df["column"] = df["calendarYear"].astype(str)+"_"+statement+"_"+df["variable"]
    df.drop(labels = ["calendarYear", "variable"], axis = 1, inplace = True)

    df = pd.pivot(df, index="symbol", columns="column", values="value")

    return df

def parsePrice(symbol, date):
    fileName = "API Archives/"+symbol+"_price_"+date+".json"
    df = pd.read_json(fileName)

    if("historical" in df):
        df["price_"+date] = df["historical"].apply(lambda x: round(x["close"], 2))
        df.drop(columns="historical", inplace=True)

    return df

def transformMarketCaps(df):
    #deprecated, if re-employing should create parameter to choose current/future date
    df = pd.pivot(df, index="symbol", columns="date", values="marketCap")
    df = df.reset_index()
    df = df.rename(columns={df.columns[1]: 'marketCap'})
    df = df.rename(columns={df.columns[-1]: 'futureMarketCap'})
    df.drop(columns = df.keys()[2:-1], inplace = True)
    return df

def prepareForTraining(df, coefficient = 1000000, columnsToExclude = []):
    df.drop(labels = "symbol", axis = 1, inplace = True)
    df = df.dropna(thresh=3)
    df = df.fillna(value=0)

    for column in columnsToExclude:
        df[column] = df[column] * coefficient
    df = df/coefficient

    return df

def buildDataset(symbols, features, labelDate, futureDate, startYear, endYear, prepare=True):
    masterdf = pd.DataFrame()

    for symbol in symbols:
        rowdf = parsePrice(symbol, labelDate)
        df = parsePrice(symbol, futureDate)

        if("price_"+labelDate not in rowdf or "price_"+futureDate not in df):
            continue

        rowdf = rowdf.merge(df, how='outer', on='symbol')   

        for statement in features:
            df = parseFinancialStatement(symbol, statement, startYear, endYear)

            rowdf = rowdf.merge(df, how='outer', on='symbol')   

        masterdf = pd.concat([masterdf, rowdf])
        
    if (prepare):
        masterdf = prepareForTraining(masterdf, columnsToExclude = ["price_2022-01-03", "price_2022-06-01"])
    return masterdf