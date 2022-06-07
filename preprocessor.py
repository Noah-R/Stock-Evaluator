import os
import pandas as pd

def getFileNames(folder):
    fileNames = []
    for file in os.listdir(folder):
        filename = os.fsdecode(file)
        fileNames.append(folder+"/"+filename)
    return fileNames

symbolList = open("stock_symbols.txt", "r")
symbols = []
for line in symbolList:
        symbols.append(str(line).strip().upper())
        
statements = ['balance-sheet', 'income-statement', 'cash-flow']

masterdf=None

for symbol in symbols:
    rowdf = None
    for statement in statements:
        fileName = "API Archives/"+symbol+"-"+statement+".json"
        df = pd.read_json(fileName)

        dropCols = ["date", "reportedCurrency", "cik", "fillingDate", "acceptedDate", "period", "link", "finalLink"]
        df.drop(labels = dropCols, axis = 1, inplace = True)

        df = df.melt(id_vars=["symbol", "calendarYear"])

        df["column"] = df["calendarYear"].astype(str)+"_"+df["variable"]
        df.drop(labels = ["calendarYear", "variable"], axis = 1, inplace = True)

        df = pd.pivot(df, index="symbol", columns="column", values="value")

        if(rowdf is None):
            rowdf=df
        else:
            rowdf = rowdf.merge(df, how='outer', on='symbol')

    masterdf = pd.concat([masterdf, rowdf])

masterdf.to_csv("results.csv")
print("done")