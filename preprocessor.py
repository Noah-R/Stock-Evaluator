import pandas as pd
import utils
import os

def transformFinancialStatement(df, startYear, endYear, statement):
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

def transformMarketCaps(df):
    df = pd.pivot(df, index="symbol", columns="date", values="marketCap")
    #todo parameter to choose current/future date
    df = df.reset_index()
    df = df.rename(columns={df.columns[1]: 'marketCap'})
    df = df.rename(columns={df.columns[-1]: 'futureMarketCap'})
    df.drop(columns = df.keys()[2:-1], inplace = True)
    return df

def transformPrice(df):
    return df

def prepareForTraining(df):
    df.drop(labels = "symbol", axis = 1, inplace = True)
    df = df/1000000
    df = df.dropna(thresh=3)
    df = df.fillna(value=0)
    return df

def buildDataset(symbols, features, target, startYear, endYear, prepare=True):#todo cleanup/functionize
    masterdf = pd.DataFrame()

    for symbol in symbols:
        fileName = "API Archives/"+symbol+"_"+target+".json"
        rowdf = pd.read_json(fileName)
        rowdf = transformPrice(rowdf)

        fileName = "API Archives/"+symbol+"_"+future+".json"
        df = pd.read_json(fileName)
        df = transformPrice(df)

        rowdf = rowdf.merge(df, how='outer', on='symbol')   

        for statement in features:
            fileName = "API Archives/"+symbol+"_"+statement+".json"
            df = pd.read_json(fileName)
            df = transformFinancialStatement(df, startYear, endYear, statement)

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