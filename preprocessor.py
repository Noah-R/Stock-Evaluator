import os
import pandas as pd

def getFileNames(folder):
    fileNames = []
    for file in os.listdir(folder):
        filename = os.fsdecode(file)
        fileNames.append(folder+"/"+filename)
    return fileNames

fileNames = getFileNames("API Archives")
for fileName in fileNames[:1]:
    df = pd.read_json(fileName)

    dropCols = ["date", "reportedCurrency", "cik", "fillingDate", "acceptedDate", "period", "link", "finalLink"]
    df.drop(labels = dropCols, axis = 1, inplace = True)

    df = df.melt(id_vars=["symbol", "calendarYear"])

    """
    symbol becomes row index

    calendarYear_variable becomes column name

    value becomes value

    result is 98 features per year
    """

    df.to_csv("example.csv")