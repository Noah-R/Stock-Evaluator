import pandas as pd
import utils
import os

def transformFinancialStatement(df, startYear, endYear):
    dropCols = ["date", "reportedCurrency", "cik", "fillingDate", "acceptedDate", "period", "link", "finalLink"]
    df.drop(labels = dropCols, axis = 1, inplace = True)

    df = df[df["calendarYear"]<=endYear]
    df = df[df["calendarYear"]>=startYear]
    df["calendarYear"] = df["calendarYear"].astype("int64")
    df = df.drop_duplicates('calendarYear')

    #for year in range(startYear, endYear+1):
    #    if(year not in set(df["calendarYear"])):
    #        print(df["symbol"].iloc[0]+" is missing a financial statement from "+str(year))

    df = df.melt(id_vars=["symbol", "calendarYear"])

    df["column"] = df["calendarYear"].astype(str)+"_"+df["variable"]
    df.drop(labels = ["calendarYear", "variable"], axis = 1, inplace = True)

    df = pd.pivot(df, index="symbol", columns="column", values="value")

    return df

def prepareForTraining(df):
    df.drop(labels = "symbol", axis = 1, inplace = True)
    df = df/1000000
    return df

def buildDataset(symbols, features, target, startYear, endYear, prepare=True):
    masterdf = pd.DataFrame()

    for symbol in symbols:
        fileName = "API Archives/"+symbol+"-"+target+".json"
        rowdf = pd.read_json(fileName)
        rowdf.drop(labels = "date", axis = 1, inplace = True)

        for statement in features:
            fileName = "API Archives/"+symbol+"-"+statement+".json"
            df = pd.read_json(fileName)
            df = transformFinancialStatement(df, startYear, endYear)

            rowdf = rowdf.merge(df, how='outer', on='symbol')

        masterdf = pd.concat([masterdf, rowdf])
        
    if (prepare):
        masterdf = prepareForTraining(masterdf)
    return masterdf

symbols = utils.readSymbols("symbols.txt")
        
features = ['balance-sheet-statement', 'income-statement', 'cash-flow-statement']
target = 'market-capitalization'

dataset = buildDataset(symbols, features, target, 2018, 2021, prepare=False)#todo prepare True before training model
#dataset = dataset.sort_index(axis=1)#uncomment to alphabetize columns
dataset.to_csv("results.csv", index=False)
print("Successfully built dataset with "+str(len(dataset))+" examples and "+str(len(dataset.keys()))+" features")