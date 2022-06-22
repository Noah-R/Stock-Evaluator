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

def parsePrice(symbol, name):
    fileName = "API Archives/"+symbol+"_"+name+".json"
    df = pd.read_json(fileName)

    if("historical" in df):
        df[name] = df["historical"].apply(lambda x: round(x["close"], 2))
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

def prepareForTraining(df):
    coefficient = 1000000

    df.drop(labels = "symbol", axis = 1, inplace = True)
    df = df.dropna(thresh=3)
    df = df.fillna(value=0)

    df["price_label"] = df["price_label"] * coefficient
    df["price_future"] = df["price_future"] * coefficient
    df = df/coefficient

    return df

def buildDataset(symbols, features, target, future, startYear, endYear, prepare=True):
    masterdf = pd.DataFrame()

    for symbol in symbols:
        rowdf = parsePrice(symbol, target)
        df = parsePrice(symbol, future)

        if(target not in rowdf or future not in df):
            continue

        rowdf = rowdf.merge(df, how='outer', on='symbol')   

        for statement in features:
            df = parseFinancialStatement(symbol, statement, startYear, endYear)

            rowdf = rowdf.merge(df, how='outer', on='symbol')   

        masterdf = pd.concat([masterdf, rowdf])
        
    if (prepare):
        masterdf = prepareForTraining(masterdf)
    return masterdf

symbols = utils.readSymbols("symbols.txt")
features = ['balance_sheet', 'income_statement', 'cash_flow']
target = 'price_label'
future = 'price_future'
startYear = 2019
endYear = 2021
prepare = True

dataset = buildDataset(symbols, features, target, future, startYear, endYear, prepare = prepare)
#dataset = dataset.sort_index(axis=1)#uncomment to alphabetize columns
dataset.to_csv("results.csv", index=False)
print("Successfully built dataset with "+str(len(dataset))+" examples and "+str(len(dataset.keys()))+" features")