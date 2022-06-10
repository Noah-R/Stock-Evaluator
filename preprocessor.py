import pandas as pd
import utils

def transformFinancialStatement(df, startYear, endYear):
    dropCols = ["date", "reportedCurrency", "cik", "fillingDate", "acceptedDate", "period", "link", "finalLink"]
    df.drop(labels = dropCols, axis = 1, inplace = True)

    df = df[df["calendarYear"]<=endYear]
    df = df[df["calendarYear"]>=startYear]
    #placeholder logic, for use if companies with short histories eventually need to be filtered out
    if(startYear not in set(df["calendarYear"])):
        print(df["symbol"].iloc[0]+" does not have financial statements from "+str(startYear))

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
    masterdf=None

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
        
features = ['balance-sheet', 'income-statement', 'cash-flow']
target = 'market-capitalization'

dataset = buildDataset(symbols, features, target, 2018, 2021)
dataset.to_csv("results.csv", index=False)
print("Successfully built dataset with "+str(len(dataset))+" examples and "+str(len(dataset.keys()))+" features")