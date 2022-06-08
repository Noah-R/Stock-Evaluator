import pandas as pd
import utils

def transformFinancialStatement(df):
    dropCols = ["date", "reportedCurrency", "cik", "fillingDate", "acceptedDate", "period", "link", "finalLink"]
    df.drop(labels = dropCols, axis = 1, inplace = True)

    df = df.melt(id_vars=["symbol", "calendarYear"])

    df["column"] = df["calendarYear"].astype(str)+"_"+df["variable"]
    df.drop(labels = ["calendarYear", "variable"], axis = 1, inplace = True)

    df = pd.pivot(df, index="symbol", columns="column", values="value")

    return df

def prepareForTraining(df):
    df.drop(labels = "symbol", axis = 1, inplace = True)
    df = df/1000000
    return df

def buildDataset(symbols, features, target, prepare=True):
    masterdf=None

    for symbol in symbols:
        fileName = "API Archives/"+symbol+"-"+target+".json"
        rowdf = pd.read_json(fileName)
        rowdf.drop(labels = "date", axis = 1, inplace = True)

        for statement in features:
            fileName = "API Archives/"+symbol+"-"+statement+".json"
            df = pd.read_json(fileName)
            df = transformFinancialStatement(df)

            rowdf = rowdf.merge(df, how='outer', on='symbol')

        masterdf = pd.concat([masterdf, rowdf])

    if (prepare):
        masterdf = prepareForTraining(masterdf)
    return masterdf

symbols = utils.readSymbols("stock_symbols.txt")
        
features = ['balance-sheet', 'income-statement', 'cash-flow']
target = 'market-capitalization'

dataset = buildDataset(symbols, features, target)
dataset.to_csv("results.csv", index=False)
print("Successfully built dataset with "+str(len(dataset))+" examples")